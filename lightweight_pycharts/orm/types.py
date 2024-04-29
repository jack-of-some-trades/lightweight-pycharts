""" Basic Types and TypeAliases """

from typing import TypeAlias, Literal, Union, Optional
from dataclasses import dataclass

# pylint: disable=line-too-long
# pylint: disable=invalid-name

HorzAlign: TypeAlias = Literal["left", "center", "right"]
VertAlign: TypeAlias = Literal["bottom", "top", "center"]
PriceFormatType: TypeAlias = Literal["price", "volume", "percent"]
DataChangedScope: TypeAlias = Literal["full", "update"]
BaseValueType: TypeAlias = Literal["price"]
LineWidth: TypeAlias = Literal[1, 2, 3, 4]

Coordinate: TypeAlias = int
UTCTimestamp: TypeAlias = int

Period: TypeAlias = Literal["s", "m", "h", "D", "W", "M", "Y"]


@dataclass
class BusinessDay:
    """
    Represents a time as a day/month/year.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/BusinessDay

    Example:
    ```
    day = BusinessDay(year=2019, month=6, day=1)  # June 1, 2019
    ```
    """

    year: int
    month: int
    day: int


Time: TypeAlias = Union[UTCTimestamp, BusinessDay, str]


# Note, this object cannot be a dataclass otherwise json.dumps()
# will dump this out as a dict. For functionality we need to call repr() on dumps()
class Color:
    """
    RBGa Color Class. To instatiate use Color.from_rgb() or Color.from_hex()
    Original Object: https://www.w3schools.com/cssref/func_rgba.php
    """

    def __init__(self, r: int, b: int, g: int, a: float):
        self._r = r
        self._b = b
        self._g = g
        self._a = a

    @classmethod
    def from_rgb(cls, r: int, b: int, g: int, a: float = 1):
        "Instantiate a new Color Instance from RGB Values"
        new_inst = cls(0, 0, 0, 0)
        # Pass variables after construction to Value Check them w/ setter funcs
        new_inst.r = r
        new_inst.g = g
        new_inst.b = b
        new_inst.a = a
        return new_inst

    @classmethod
    def from_hex(cls, hex_value: str):
        "Instantiate a new Color Instance from a hex string of 3, 4, 6, or 8 chars."
        hex_value = hex_value.lstrip("#")
        if len(hex_value) == 6 or len(hex_value) == 8:
            # Hex String of 6 or 8 Chars
            r, g, b = [int(hex_value[i : i + 2], 16) for i in (0, 2, 4)]
            alpha = 1 if (len(hex_value) != 8) else int(hex_value[6:8], 16) / 255

        elif len(hex_value) == 3 or len(hex_value) == 4:
            # Hex String of 3 or 4 Chars
            r, g, b = [
                ((int(char, 16) << 4) + (int(char, 16))) for char in hex_value[0:3]
            ]
            alpha = (
                1
                if (len(hex_value) != 4)
                else ((int(hex_value[3], 16) << 4) + int(hex_value[3], 16)) / 255
            )
        else:
            raise ValueError(f"Hex Color of length {len(hex_value)} is not valid.")
        return cls(r, g, b, alpha)

    # @classmethod
    # def from_jdict(cls, j_dict: dict):
    #     "Instantiate a new Color Instance from a Loaded JSON Dict"
    #     raise NotImplementedError

    # region // -------------- Color Getters & Setters -------------- //
    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, r: int):
        if r > 255:
            raise ValueError(f"Arg: {r = } is not valid. Max Value is 255.")
        if r < 0:
            raise ValueError(f"Arg: {r = } is not valid. Min Value is 0.")
        self._r = r

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, g: int):
        if g > 255:
            raise ValueError(f"Arg: {g = } is not valid. Max Value is 255.")
        if g < 0:
            raise ValueError(f"Arg: {g = } is not valid. Min Value is 0.")
        self._g = g

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, b: int):
        if b > 255:
            raise ValueError(f"Arg: {b = } is not valid. Max Value is 255.")
        if b < 0:
            raise ValueError(f"Arg: {b = } is not valid. Min Value is 0.")
        self._b = b

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, a: float):
        if a > 1:
            raise ValueError(f"Arg: {a = } is not valid. Max Value is 1.")
        if a < 0:
            raise ValueError(f"Arg: {a = } is not valid. Min Value is 0.")
        self._a = a

    # endregion

    def __repr__(self):
        "Javascript RGBA Representation of Class Params."
        return f"rgba({self._r},{self._g},{self._b},{self._a})"


@dataclass
class TF:
    "Dataclass Representation of a Timeframe"
    _mult: int
    _period: Period

    def __init__(self, mult: int, period: Period):
        self.validate(mult, period)
        self._period = period
        self._mult = mult

    def __str__(self) -> str:
        return self.toString

    # region ---- TF Setters and Getters ----

    @property
    def mult(self):
        return self._mult

    @mult.setter
    def amount(self, value: int):
        self.validate(value, self._period)
        self._mult = value

    @property
    def period(self) -> str:
        return self._period

    @period.setter
    def period(self, value: Period):
        self.validate(self._mult, value)
        self._period = value

    @property
    def toString(self) -> str:
        return f"{self._mult}{self._period}"

    @staticmethod
    def validate(amount: int, unit: Period):
        if amount <= 0:
            raise ValueError(
                f"Timeframe Period Multiplier,{amount}, must be a positive value."
            )
        if amount != round(amount):
            raise ValueError(
                f"Timeframe Period Multiplier,{amount}, must be an integer value."
            )

        match unit:
            case "s" | "m":
                if amount > 59:
                    raise ValueError("Seconds & Minutes multiplier must be in [1, 59].")
            case "h":
                if amount > 23:
                    raise ValueError("Hour multiplier must be in [1, 23].")
            case "D":
                if amount > 6:
                    raise ValueError("Hour multiplier must be in [1, 6].")
            case "W":
                if amount > 3:
                    raise ValueError("Hour multiplier must be in [1, 3].")
            case "M":
                if amount not in (1, 2, 3, 6):
                    raise ValueError("Month units must be (1, 2, 3, 6)")
            case "Y":
                return
            case _:
                raise ValueError(f"'{unit}' Not a valid timeframe period.")

    @property
    def unix_len(self) -> int:
        """
        The length, in seconds, that the timeframe represents.

        1 Month = 30.44 Days, 1 Year = 365.24 Days (Unix Standard Conversions)
        """
        match self._period:
            case "s":
                return self._mult
            case "m":
                return self._mult * 60
            case "h":
                return self._mult * 3600
            case "D":
                return self._mult * 86400
            case "W":
                return self._mult * 604800
            case "M":
                return self._mult * 2629743
            case "Y":
                return self._mult * 31556926
            case _:
                return -1

    # endregion


# region --------------------------------------- Lightweight Chart interface Dataclasses --------------------------------------- #

# pylint: disable="wrong-import-position"
# Moving the Import to here fixes a circular import error w/Color
from .enum import ColorType, SeriesMarkerShape, SeriesMarkerPosition

# Some of these will likely not be used unless further Javascript <-> Python integeration
# is done; specifically around passing MouseEvents and Timeframe Changes back to Python.


@dataclass
class SolidColor:
    """
    Represents a solid color.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/SolidColor
    """

    type: Literal[ColorType.Solid]
    color: Optional[Color] = None


@dataclass
class VerticalGradientColor:
    """
    Represents a vertical gradient of two colors.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/VerticalGradientColor
    """

    type: Literal[ColorType.VerticalGradient]
    topColor: Optional[Color] = None
    bottomColor: Optional[Color] = None


@dataclass
class BaseValuePrice:
    """
    Represents a type of priced base value of baseline series type.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/BaseValuePrice
    """

    price: float
    type: BaseValueType = "price"


@dataclass
class PriceFormat:  # Actually PriceFormatBuiltIn. True PriceFormat is Union [PriceFormatBuiltIn | PriceFormatCustom]
    """
    Represents series value formatting options.
    The precision and minMove properties allow wide customization of formatting.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/PriceFormatBuiltIn

    Docs Reference the Built-in Values only, PriceFormatCustom is not implemented here
    """

    type: PriceFormatType = "price"
    precision: int = 2
    minMove: float = 0.01


# @dataclass
# class PriceFormatCustom:
#     """
#     Represents series value formatting options.
#     Removed to keep JS Functions in JS Files. May enable later on though
#     Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/PriceFormatCustom
#     """

#     type = Literal["custom"]
#     minMove: float = 0.01
#     formatter: PriceFormatterFn


@dataclass
class TimeRange:
    """
    Represents a Time range `from` one value `to` another.
    """

    from_: Time
    to_: Time


@dataclass
class BarsInfo(TimeRange):
    """
    Represents a range of bars and the number of bars outside the range.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/BarsInfo
    """

    barsBefore: int
    barsAfter: int


@dataclass
class Point:
    """
    Represents a point on the chart.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/Point
    """

    x: float
    y: float


@dataclass
class TouchMouseEventData:
    """
    The TouchMouseEventData class represents events that occur due to the user interacting with a
    pointing device (such as a mouse).
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/TouchMouseEventData
    """

    clientX: Coordinate
    clientY: Coordinate
    pageX: Coordinate
    pageY: Coordinate
    screenX: Coordinate
    screenY: Coordinate
    localX: Coordinate
    localY: Coordinate
    ctrlKey: bool
    altKey: bool
    shiftKey: bool
    metaKey: bool


@dataclass
class MouseEventParams:
    """
    Represents a mouse event.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/MouseEventParams
    """

    time: Optional[Time] = None
    logical: Optional[int] = None
    point: Optional[Point] = None
    # Likely will not implement since these aren't really functional in the API
    # series_data = {}
    # hovered_series: Optional[str] = None
    hovered_object_id: Optional[str] = None
    source_event: Optional[TouchMouseEventData] = None


@dataclass
class TickMark:
    """
    Tick mark for the horizontal scale.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/TickMark
    """

    index: int
    time: Time
    weight: float
    original_time: Time


@dataclass
class TimeMark:
    """
    Represents a tick mark on the horizontal (time) scale.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/TimeMark
    """

    need_align_coordinate: bool
    coord: int
    label: str
    weight: float


@dataclass
class TimeScalePoint:
    """
    Represents a point on the time scale.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/TimeScalePoint
    """

    time: Time
    timeWeight: float
    originalTime: Time


@dataclass
class SeriesMarker:
    """
    Represents a series marker.
    Docs: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/SeriesMarker
    """

    time: Time
    shape: SeriesMarkerShape
    position: SeriesMarkerPosition
    id: Optional[str] = None
    size: Optional[int] = 1
    color: Optional[Color] = None
    text: Optional[str] = None


# endregion