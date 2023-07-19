# %%
# Imports
from typing import List
import attr


# %%
# Class definitions
@attr.s
class Word:
    bounding_box: List[int] = attr.ib()
    text: str = attr.ib()


@attr.s
class Line:
    bounding_box: List[int] = attr.ib()
    words: List[Word] = attr.ib(factory=list)

    @staticmethod
    def from_dict(data: dict) -> "Line":
        words = [Word(**word) for word in data["words"]]
        return Line(data["boundingBox"], words)


@attr.s
class Region:
    bounding_box: List[int] = attr.ib()
    lines: List[Line] = attr.ib(factory=list)

    @staticmethod
    def from_dict(data: dict) -> "Region":
        lines = [Line.from_dict(line) for line in data["lines"]]
        return Region(data["boundingBox"], lines)


@attr.s
class Page:
    regions: List[Region] = attr.ib(factory=list)

    @staticmethod
    def from_dict(data: dict) -> "Page":
        regions = [Region.from_dict(region) for region in data["regions"]]
        return Page(regions)


@attr.s
class Document:
    pages: List[Page] = attr.ib(factory=list)

    @staticmethod
    def from_json(data: dict) -> "Document":
        pages = [Page.from_dict(page) for page in data["pages"]]
        return Document(pages)


# %%
# Test
