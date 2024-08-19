""" Python Classes that handle the various GUI Widgets """

from __future__ import annotations
import logging
import asyncio
import multiprocessing as mp
from functools import partial
from dataclasses import asdict
from typing import Literal, Optional

import pandas as pd

from lightweight_pycharts.orm.types import TF, Color

from . import orm
from . import util
from . import indicators
from . import indicator as ind
from .orm import layouts, Symbol
from .events import Events, Emitter, Socket_Switch_Protocol
from .js_api import PyWv, MpHooks
from .js_cmd import JS_CMD, PY_CMD
from .orm.series import AnyBasicData, SeriesType, SingleValueData


logger = logging.getLogger("lightweight-pycharts")


class Window:
    """Window is an object that handles the Javascript Webview Object
    This window creates and handels a Javascript implementation of:
        - Application Frame     *TBI
        - Window Tabs           *TBI
        - Toolbar               *TBI
        - Search Bar            *TBI
        - Interval Switcher     *TBI
        - Watchlist, etc.       *TBI

    Window contains a 'Container' object for every tab.
    """

    def __init__(
        self,
        *,
        daemon: bool = True,
        events: Optional[Events] = None,
        log_level: Optional[logging._Level] = None,
        options: Optional[orm.options.PyWebViewOptions] = None,
        **kwargs,
    ) -> None:
        # -------- Setup and start the Pywebview subprocess  -------- #
        if options is not None:
            # PyWebviewOptions Given, overwrite anything in kwargs.
            kwargs = asdict(options)

        if log_level is not None:
            logger.setLevel(log_level)
            kwargs["log_level"] = log_level
        elif "debug" in kwargs.keys() and kwargs["debug"]:
            logger.setLevel(logging.DEBUG)

        # create and then unpack the hooks directly into class variables
        mp_hooks = MpHooks()
        self._fwd_queue = mp_hooks.fwd_queue
        self._rtn_queue = mp_hooks.rtn_queue
        self._start_event = mp_hooks.start_event
        self._stop_event = mp_hooks.stop_event
        self._js_loaded_event = mp_hooks.js_loaded_event

        kwargs["mp_hooks"] = mp_hooks  # Pass the hooks along to PyWv
        self._view_process = mp.Process(target=PyWv, kwargs=kwargs, daemon=daemon)
        self._view_process.start()

        # Wait for PyWebview to load before continuing
        # js_loaded_event set in PyWv._assign_callbacks()
        if not self._js_loaded_event.wait(timeout=10):
            raise TimeoutError(
                "Failed to load PyWebView in a reasonable amount of time."
            )

        # Begin Listening for any responses from PyWV Process
        self._queue_manager = asyncio.create_task(self._manage_queue())

        # -------- Create Subobjects  -------- #
        if events is not None:
            self.events = events
        else:
            self.events = Events()
        self.events.symbol_search.response = partial(
            self._symbol_search_rsp, fwd_queue=self._fwd_queue
        )
        self.events.data_request.response = partial(
            self._data_request_rsp, socket_switch=self.events.socket_switch
        )

        # Using ID_List over ID_Dict so element order is mutable for PY_CMD.REORDER_CONTAINERS
        self._container_ids = util.ID_List("c")
        self.containers: list[Container] = []

    # region ------------------------ Private Window Methods  ------------------------ #

    def _execute_cmd(self, cmd: PY_CMD, *args):
        logger.debug("PY_CMD: %s: %s", cmd.name, str(args))
        # If this CMD list gets very large then it might be worth making another CMD_ROLODEX.
        # High dependence on window instance variables is keeping this as a Match Statement ATM.
        match cmd, *args:
            case PY_CMD.SYMBOL_SEARCH, str(), bool(), list(), list(), list():
                self.events.symbol_search(
                    ticker=args[0],
                    confirmed=args[1],
                    types=args[2],
                    brokers=args[3],
                    exchanges=args[4],
                )

            case PY_CMD.DATA_REQUEST, str(), str(), orm.Symbol(), orm.TF():
                frame = self.get_container(args[0]).frames[args[1]]
                kwargs = {
                    "series": frame.main_series,
                    "symbol": args[2],
                    "timeframe": args[3],
                }
                self.events.data_request(symbol=args[2], tf=args[3], rsp_kwargs=kwargs)

            case PY_CMD.LAYOUT_CHANGE, str(), orm.enum.layouts():
                container = self.get_container(args[0])
                container.set_layout(args[1])

            case PY_CMD.SERIES_CHANGE, str(), str(), orm.series.SeriesType():
                frame = self.get_container(args[0]).frames[args[1]]
                frame.main_series.change_series_type(args[2])

            case PY_CMD.SET_INDICATOR_OPTS, str(), str(), str(), dict():
                indicator = (
                    self.get_container(args[0]).frames[args[1]].indicators[args[2]]
                )
                indicator.__parse_options_dict__(args[3])

            case PY_CMD.ADD_CONTAINER:
                self.new_tab()

            case PY_CMD.REMOVE_CONTAINER, str():
                self.del_tab(args[0])

            case PY_CMD.REORDER_CONTAINERS, int(), int():
                # This keeps the Window Obj Tab order identical to what is displayed
                self._container_ids.insert(args[1], self._container_ids.pop(args[0]))
                self.containers.insert(args[1], self.containers.pop(args[0]))

    async def _manage_queue(self):
        logger.debug("Entered Async Queue Manager")
        while not self._stop_event.is_set():
            if self._rtn_queue.empty():
                await asyncio.sleep(0.05)
            else:
                msg = self._rtn_queue.get()
                if isinstance(msg, tuple):
                    cmd, *rsp = msg
                else:
                    cmd = msg
                    rsp = tuple()
                self._execute_cmd(cmd, *rsp)
                # logger.debug("Window Recieved Command: %s: %s", cmd, rsp)
        logger.debug("Exited Async Queue Manager")

    # endregion

    # region ------------------------ Private Event Response Methods ------------------------ #

    @staticmethod
    def _symbol_search_rsp(items: list[orm.types.Symbol], *_, fwd_queue: mp.Queue):
        fwd_queue.put((JS_CMD.SET_SYMBOL_ITEMS, items))

    @staticmethod
    def _data_request_rsp(
        data: Optional[pd.DataFrame],
        *_,
        series: indicators.Series,
        symbol: orm.Symbol,
        timeframe: orm.TF,
        socket_switch: Emitter[Socket_Switch_Protocol],  # Set by Partial Func
    ):
        # Close the socket if there was a symbol change
        if series.socket_open and series.symbol != symbol:
            socket_switch(state="close", symbol=series.symbol, series=series)

        if data is not None:
            # Set Data *before* series.update_data can be called
            series.set_data(data, symbol=symbol)
            if not series.socket_open:
                socket_switch(state="open", symbol=symbol, series=series)
        else:
            if series.socket_open:
                # Closes the socket if an invalid timeframe was selected.
                socket_switch(state="close", symbol=series.symbol, series=series)
            # Clear Data *after* Socket close so socket close gets passed the old symbol
            series.clear_data(timeframe, symbol)

    # endregion

    # region ------------------------ Public Window Methods  ------------------------ #

    def show(self):
        "Show the View Window"
        self._fwd_queue.put(JS_CMD.SHOW)

    def hide(self):
        "Hide the View Window"
        self._fwd_queue.put(JS_CMD.HIDE)

    def maximize(self):
        "Hide the View Window"
        self._fwd_queue.put(JS_CMD.MAXIMIZE)

    def minimize(self):
        "Hide the View Window"
        self._fwd_queue.put(JS_CMD.MINIMIZE)

    def restore(self):
        "Hide the View Window"
        self._fwd_queue.put(JS_CMD.RESTORE)

    def close(self):
        "Hide the View Window"
        self._fwd_queue.put(JS_CMD.CLOSE)

    async def await_close(self):
        "Await closure of the window's asyncio loop. (Window Closure)"
        await self._queue_manager

    def load_css(self, filepath: str):
        "Pass a .css file's absolute filepath to the window to load it"
        self._fwd_queue.put((JS_CMD.LOAD_CSS, filepath))

    def set_user_colors(self, opts: list[Color]):
        "Set the User Defined Colors available in the Color Picker"
        self._fwd_queue.put((JS_CMD.SET_USER_COLORS, opts))

    def new_tab(self) -> Container:
        "Add a new Tab. A reference to the new Container is returned"
        new_id = self._container_ids.generate_id()
        new_container = Container(new_id, self._fwd_queue, self)
        self.containers.append(new_container)
        return new_container

    def del_tab(self, _id: str | int):
        "Deletes a Tab. Id can be either the js_id or tab #."
        container = self.get_container(_id)

        # Be sure to allow indicators to clear themselves
        # This ensures web-sockets and other assets are closed.
        for frame in container.frames.values():
            for indicator in frame.indicators.copy().values():
                indicator.delete()

        # Remove the Objects from local storable and erase their JS global references
        self._container_ids.remove(container.js_id)
        self.containers.remove(container)
        self._fwd_queue.put((JS_CMD.REMOVE_CONTAINER, container.js_id))
        self._fwd_queue.put((JS_CMD.REMOVE_REFERENCE, *container.all_ids()))

    def get_container(self, _id: int | str) -> Container:
        "Return the container that matches either the given js_id, or the tab #"
        if isinstance(_id, str):
            for container in self.containers:
                if _id == container.js_id:
                    return container
            raise IndexError(f"Window doesn't have a Container with ID:{_id}")
        else:
            if 0 <= _id < len(self.containers):
                return self.containers[_id]
            raise IndexError(f"Container index {_id} out of bounds.")

    def set_search_filters(
        self,
        category: Literal["security_type", "data_broker", "exchange"],
        items: list[str],
    ):
        "Set the available search filters in the symbol search menu."
        self._fwd_queue.put((JS_CMD.SET_SYMBOL_SEARCH_OPTS, category, items))

    def set_layout_favs(self, favs: list[orm.layouts]):
        "Set the layout types shown on the Window's TopBar"
        self._fwd_queue.put((JS_CMD.UPDATE_LAYOUT_FAVS, {"favorites": favs}))

    def set_series_favs(self, favs: list[orm.series.SeriesType]):
        "Set the Series types shown on the Window's TopBar"
        self._fwd_queue.put((JS_CMD.UPDATE_SERIES_FAVS, {"favorites": favs}))

    def set_timeframes(self, favs: list[orm.TF], opts: Optional[list[orm.TF]] = None):
        "Set the Timeframes shown on the Window's TopBar and in the dropdown menu"
        menu_opts = {}
        if opts is not None:
            for fav in favs:
                if fav not in opts:
                    opts.append(fav)

            for option in opts:
                if option.period in menu_opts:
                    menu_opts[option.period] += [option.mult]
                else:
                    menu_opts[option.period] = [option.mult]
        else:
            menu_opts = {
                "s": [1, 2, 5, 15, 30],
                "m": [1, 2, 5, 15, 30],
                "h": [1, 2, 4],
                "D": [1],
                "W": [1],
            }
        json_dict = {
            "menu_listings": menu_opts,
            "favorites": [tf.toString for tf in favs],
        }
        self._fwd_queue.put((JS_CMD.UPDATE_TF_OPTS, json_dict))

    # endregion


class Container:
    "A Container Class instance manages the all sub frames and the layout that contains them."

    def __init__(self, _js_id: str, fwd_queue: mp.Queue, window: Window) -> None:
        self._fwd_queue = fwd_queue
        self._window = window
        self._js_id = _js_id
        self.layout_type = layouts.SINGLE
        self.frames = util.ID_Dict[Frame](f"{_js_id}_f")

        self._fwd_queue.put((JS_CMD.ADD_CONTAINER, self._js_id))
        self.set_layout(self.layout_type)  # Adds First Frame

    def __del__(self):
        logger.debug("Deleteing Container: %s", self._js_id)

    @property
    def js_id(self) -> str:
        "Immutable Copy of the Object's Javascript_ID"
        return self._js_id

    def add_frame(self, _js_id: Optional[str] = None) -> Frame:
        "Creates a new Frame. Frame will only be displayed once the layout supports a new frame."
        return Frame(self, _js_id)

    def set_layout(self, layout: layouts):
        "Set the layout of the Container creating Frames as needed"
        # If there arent enough Frames to support the layout then generate them
        frame_diff = len(self.frames) - layout.num_frames
        if frame_diff < 0:
            for _ in range(-frame_diff):
                logger.debug("Add Frame")
                self.add_frame()

        self._fwd_queue.put((JS_CMD.SET_LAYOUT, self._js_id, layout))
        self.layout_type = layout

    def all_ids(self) -> list[str]:
        "Return a List of all Ids of this object and sub-objects"
        _ids = [self._js_id]
        for _, frame in self.frames.items():
            _ids += frame.all_ids()
        return _ids


class Frame:
    """
    Frame Objects primarily hold information about the timeseries that is being displayed. They
    retain a copy of data that is used across all sub-panes as well as the references to said panes.

    ** ATM this class translates to a Chart_Frame in the Frontend. At some point in the future this
    will become a Chart_Frame that inherits from an Abstract Frame class. That implementation will
    match the current Frontend implementation and allow for 'Frame' to be an abstract re-sizeable
    viewport in the window. Broker integration, Bid/Ask Tables, Stock Screeners... Sky's the limit.
    """

    def __init__(self, parent: Container, _js_id: Optional[str] = None) -> None:
        if _js_id is None:
            self._js_id = parent.frames.generate_id(self)
        else:
            self._js_id = parent.frames.affix_id(_js_id, self)

        self._window = parent._window
        self._fwd_queue = parent._fwd_queue
        self.panes = util.ID_Dict[Pane](f"{self._js_id}_p")
        self.indicators = util.ID_Dict[ind.Indicator]("i")
        # Indicators append themselves to this ID_Dict. See Indicator DocString for reasoning.

        self._fwd_queue.put((JS_CMD.ADD_FRAME, self._js_id, parent._js_id))

        # Add main pane and Series, neither should ever be deleted
        self.add_pane(Pane.__special_id__)
        indicators.Series(self, js_id=indicators.Series.__special_id__)

    def __del__(self):
        for indicator in self.indicators.copy().values():
            indicator.delete()
        logger.debug("Deleteing Frame: %s", self._js_id)

    # region ------------- Dunder Control Functions ------------- #

    def __set_displayed_symbol__(self, symbol: Symbol):
        "*Does not change underlying data*"
        self._fwd_queue.put((JS_CMD.SET_FRAME_SYMBOL, self._js_id, symbol))

    def __set_displayed_timeframe__(self, timeframe: TF):
        "*Does not change underlying data*"
        self._fwd_queue.put((JS_CMD.SET_FRAME_TIMEFRAME, self._js_id, timeframe))

    def __set_displayed_series_type__(self, series_type: SeriesType):
        "*Does not change underlying data*"
        self._fwd_queue.put((JS_CMD.SET_FRAME_SERIES_TYPE, self._js_id, series_type))

    def __set_whitespace__(self, data: pd.DataFrame, p_data: SingleValueData):
        self._fwd_queue.put((JS_CMD.SET_WHITESPACE_DATA, self._js_id, data, p_data))

    def __clear_whitespace__(self):
        self._fwd_queue.put((JS_CMD.CLEAR_WHITESPACE_DATA, self._js_id))

    def __update_whitespace__(self, data: AnyBasicData, p_data: SingleValueData):
        self._fwd_queue.put((JS_CMD.UPDATE_WHITESPACE_DATA, self._js_id, data, p_data))

    # endregion

    def add_pane(self, js_id: Optional[str] = None) -> Pane:
        "Add a Pane to the Current Frame"
        return Pane(self, js_id)  # Pane Appends itself to Frame.panes

    def all_ids(self) -> list[str]:
        "Return a List of all Ids of this object and sub-objects"
        return [self._js_id] + self.all_pane_ids()

    def all_pane_ids(self) -> list[str]:
        "Return a List of all Panes Ids of this object"
        return list(self.panes.keys())

    @property
    def js_id(self) -> str:
        "Immutable Copy of the Object's Javascript_ID"
        return self._js_id

    @property
    def main_pane(self) -> Pane:
        "Main Display Pane of the Frame"
        return self.panes[self.panes.prefix + Pane.__special_id__]

    @property
    def main_series(self) -> indicators.Series:
        "Series Indicator that contain's the Frame's main symbol data"
        main_series = self.indicators[
            self.indicators.prefix + indicators.Series.__special_id__
        ]
        if isinstance(main_series, indicators.Series):
            return main_series
        raise AttributeError(f"Cannot find Main Series for Frame {self._js_id}")

    # region ------------- Indicator Functions ------------- #

    def get_indicators_of_type[T: ind.Indicator](self, _type: type[T]) -> dict[str, T]:
        "Returns a Dictionary of Indicators applied to this Frame that are of the Given Type"
        rtn_dict = {}
        for _key, _ind in self.indicators.items():
            if isinstance(_ind, _type):
                rtn_dict[_key] = _ind
        return rtn_dict

    def remove_indicator(self, _id: str | int):
        "Remove and Delete an Indicator"
        try:
            self.indicators[_id].delete()
        except (KeyError, IndexError):
            logger.warning(
                "Could not delete Indicator '%s'. It does not exist on frame '%s'",
                _id,
                self._js_id,
            )

    # endregion


class Pane:
    """
    An individual charting window, can contain seriesCommon objects and indicators.
    """

    __special_id__ = "main"  # Must match Pane.ts Special ID

    def __init__(self, parent: Frame, js_id: Optional[str] = None) -> None:
        if js_id is None:
            self._js_id = parent.panes.generate_id(self)
        else:
            self._js_id = parent.panes.affix_id(js_id, self)

        self._window = parent._window
        self._fwd_queue = parent._fwd_queue
        self.__main_pane__ = self._js_id == Pane.__special_id__

        self._fwd_queue.put((JS_CMD.ADD_PANE, self._js_id, parent._js_id))

    @property
    def js_id(self) -> str:
        "Immutable Copy of the Object's Javascript_ID"
        return self._js_id

    def add_primitive(self):
        """TBD?"""
        raise NotImplementedError
