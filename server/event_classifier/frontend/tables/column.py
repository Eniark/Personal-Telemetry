from dataclasses import dataclass

# This class contains metadata about a column
@dataclass(slots=True, frozen=True)
class Column:
    title: str
    width: int|None = None # use the default PyQt width
    hidden: bool|None = False
    text_alignment: str = 'left'