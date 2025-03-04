from dataclasses import dataclass, field
from typing import Literal, Any

@dataclass(init=True, order=True, repr=True, frozen=True)
class Parameter():
    name: str
    path: str
    min_value: Any
    max_value: Any
    type: Literal['scalar', 'vector', 'element'] = 'vector'
    index: list[int] = field(default_factory=lambda: [0])
    length: int = 1
    copy_to_path: str = ''
    copy_to_index: list[list[int]] = field(default_factory=lambda: [[0]]) 

    def __post_init__(self):
        if isinstance(self.min_value, float):
            object.__setattr__(self, 'min_value', [self.min_value] * self.length)
        if isinstance(self.max_value, float):
            object.__setattr__(self, 'max_value', [self.max_value] * self.length)
        assert(self.type in ['scalar', 'vector', 'element'])
        if self.type == 'element': 
            assert(len(self.index) == self.length)

    @property
    def names(self):
        if self.type == 'vector' and self.length != 1: 
            return [ f"{self.name}[{num}]" for num in range(self.length) ]
        elif self.type == 'element' and self.length != 1:
            return [ f"{self.name}[{num}]" for num in self.index ]
        else: 
            return [ self.name ]
