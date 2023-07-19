from typing import List, Optional
import attr
from attr.validators import instance_of
import json

from fitz import Point as FitzPoint

SCALES = {"inch": 72, "mm": 2.83465, "pixel": 1}


@attr.s
class Point:
    x: float = attr.ib(converter=float)
    y: float = attr.ib(converter=float)

    def to_fitz(self, scale: str) -> FitzPoint:
        return FitzPoint(self.x * SCALES[scale], self.y * SCALES[scale])


@attr.s
class BoundingBox:
    points: List[Point] = attr.ib()

    @staticmethod
    def from_json(lst: list[float]) -> "BoundingBox":
        points = [Point(x=lst[i], y=lst[i + 1]) for i in range(0, len(lst), 2)]
        return BoundingBox(points=points)

    def draw(self, page, scale: str = "inch", color: tuple = (0, 0, 1)):
        points = [point.to_fitz(scale) for point in self.points]
        annot = page.add_polygon_annot(points)
        annot.set_border(width=0.3, dashes=[2])
        annot.set_colors(stroke=color)
        annot.update()


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
