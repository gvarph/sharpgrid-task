from typing import List, Optional
import attr
from attr.validators import instance_of
import json

from fitz import Point as FitzPoint


@attr.s
class Point:
    x: float = attr.ib(converter=float)
    y: float = attr.ib(converter=float)


@attr.s
class BoundingBox:
    scales = {"inch": 72, "mm": 2.83465, "pixel": 1}
    top_left: Point = attr.ib()
    top_right: Point = attr.ib()
    bottom_right: Point = attr.ib()
    bottom_left: Point = attr.ib()

    @staticmethod
    def from_json(lst: list[float]) -> "BoundingBox":
        return BoundingBox(
            top_left=Point(x=lst[0], y=lst[1]),
            top_right=Point(x=lst[2], y=lst[3]),
            bottom_right=Point(x=lst[4], y=lst[5]),
            bottom_left=Point(x=lst[6], y=lst[7]),
        )

    def _calculate_point(self, point: Point, page_height: int, scale: str) -> FitzPoint:
        x = point.x * self.scales[scale]
        y = page_height - point.y * self.scales[scale]
        return FitzPoint(x, y)

    def to_fitz_points(self, page_height: int, scale: str = "inch") -> List[FitzPoint]:
        return [
            self._calculate_point(self.top_left, page_height, scale),
            self._calculate_point(self.top_right, page_height, scale),
            self._calculate_point(self.bottom_right, page_height, scale),
            self._calculate_point(self.bottom_left, page_height, scale),
        ]


@attr.s
class Word:
    text: str = attr.ib()
    bounding_box: BoundingBox = attr.ib()
    confidence: Optional[str] = attr.ib(default=None)


@attr.s
class Line:
    text: str = attr.ib()
    bounding_box: BoundingBox = attr.ib()
    words: List[Word] = attr.ib(factory=list)

    @staticmethod
    def from_json(data: dict) -> "Line":
        return Line(
            bounding_box=BoundingBox.from_json(data["boundingBox"]),
            words=[
                Word(
                    bounding_box=BoundingBox.from_json(word["boundingBox"]),
                    text=word["text"],
                )
                for word in data["words"]
            ],
            text=data["text"],
        )


@attr.s
class MenuPage:
    page_num: int = attr.ib(validator=instance_of(int))
    clockwise_orientation: float = attr.ib()
    width: float = attr.ib(converter=float)
    height: float = attr.ib(converter=float)
    unit: str = attr.ib()
    lines: List[Line] = attr.ib(factory=list)

    @staticmethod
    def from_json(data: dict) -> "MenuPage":
        return MenuPage(
            page_num=data["page"],
            clockwise_orientation=data["clockwiseOrientation"],
            width=data["width"],
            height=data["height"],
            unit=data["unit"],
            lines=[Line.from_json(line) for line in data["lines"]],
        )


@attr.s
class Menu:
    status: str = attr.ib()
    pages: List[MenuPage] = attr.ib(factory=list)

    @staticmethod
    def from_json(data: dict) -> "Menu":
        recognition_results = [
            MenuPage.from_json(page) for page in data["recognitionResults"]
        ]
        return Menu(status=data["status"], pages=recognition_results)

    @staticmethod
    def from_json_file(path: str) -> "Menu":
        with open(path) as file:
            return Menu.from_json(json.load(file))
