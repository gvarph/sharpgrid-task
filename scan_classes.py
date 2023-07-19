from typing import List, Optional
import attr
from attr.validators import instance_of
import json


@attr.s
class Point:
    x: float = attr.ib(converter=float)
    y: float = attr.ib(converter=float)


@attr.s
class BoundingBox:
    top_left: Point = attr.ib()
    top_right: Point = attr.ib()
    bottom_right: Point = attr.ib()
    bottom_left: Point = attr.ib()

    @staticmethod
    def from_lst(lst: list[float]) -> "BoundingBox":
        return BoundingBox(
            top_left=Point(x=lst[0], y=lst[1]),
            top_right=Point(x=lst[2], y=lst[3]),
            bottom_right=Point(x=lst[4], y=lst[5]),
            bottom_left=Point(x=lst[6], y=lst[7]),
        )


@attr.s
class BoundingBoxedObject:
    bounding_box: BoundingBox = attr.ib()


@attr.s
class Word(BoundingBoxedObject):
    text: str = attr.ib()
    confidence: Optional[str] = attr.ib(default=None)


@attr.s
class Line(BoundingBoxedObject):
    text: str = attr.ib()
    words: List[Word] = attr.ib(factory=list)

    @staticmethod
    def from_dict(data: dict) -> "Line":
        return Line(
            bounding_box=BoundingBox.from_lst(data["boundingBox"]),
            words=[
                Word(
                    bounding_box=BoundingBox.from_lst(word["boundingBox"]),
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
    def from_dict(data: dict) -> "MenuPage":
        return MenuPage(
            page_num=data["page"],
            clockwise_orientation=data["clockwiseOrientation"],
            width=data["width"],
            height=data["height"],
            unit=data["unit"],
            lines=[Line.from_dict(line) for line in data["lines"]],
        )


@attr.s
class Menu:
    status: str = attr.ib()
    pages: List[MenuPage] = attr.ib(factory=list)

    @staticmethod
    def from_dict(data: dict) -> "Menu":
        recognition_results = [
            MenuPage.from_dict(page) for page in data["recognitionResults"]
        ]
        return Menu(status=data["status"], pages=recognition_results)

    @staticmethod
    def from_json_file(path: str) -> "Menu":
        return Menu.from_dict(json.load(open(path)))
