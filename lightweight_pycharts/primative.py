"Python Object Representations of Primitive HTML Canvas drawing objects"

from typing import Any, Optional, TYPE_CHECKING
from dataclasses import dataclass
from abc import ABCMeta


from .js_cmd import JS_CMD
from .orm.series import SingleValueData

from .orm.types import JS_Color

if TYPE_CHECKING:
    from .indicator import Indicator

# pylint: disable=invalid-name


class Primitive(metaclass=ABCMeta):

    def __init__(
        self,
        parent: "Indicator",
        args: dict[str, Any],
        js_id: Optional[str] = None,
        display_pane_id: Optional[str] = None,
    ) -> None:

        if display_pane_id is None:
            display_pane_id = parent._ids[0]

        if js_id is None:
            self._js_id = parent._primitives.generate_id(self)
        else:
            self._js_id = parent._primitives.affix_id(js_id, self)

        self._ids = display_pane_id, parent.js_id, self._js_id
        self._fwd_queue = parent._fwd_queue

        self._fwd_queue.put(
            (JS_CMD.ADD_PRIMITIVE, *self._ids, self.__class__.__name__, args)
        )


class TrendLine(Primitive):

    p1: SingleValueData
    p2: SingleValueData

    def __init__(self, parent: "Indicator", p1: SingleValueData, p2: SingleValueData):
        init_args = {"p1": p1, "p2": p2}
        super().__init__(parent, init_args)

    @dataclass
    class Options:
        width: Optional[int] = None
        autocale: Optional[bool] = None
        show_labels: Optional[bool] = None
        lineColor: Optional[JS_Color] = None
        labeltextColor: Optional[JS_Color] = None
        labelBackgroundColor: Optional[JS_Color] = None