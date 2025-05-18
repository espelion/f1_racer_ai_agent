from enum import Enum
import re
from typing import Optional

class Stage(Enum):
    FP1 = "Free Practice 1"
    FP2 = "Free Practice 2"
    FP3 = "Free Practice 3"
    Q1 = "Qualifying 1"
    Q2 = "Qualifying 2"
    Q3 = "Qualifying 3"
    RACE = "The Grand Prix (Race)"

    def __str__(self):
        return self.value

    @property
    def short_name(self):
        if "Practice" in self.value:
            return f"FP{self.name[-1]}"
        elif "Qualifying" in self.value:
            return f"Q{self.name[-1]}"
        elif self == Stage.RACE:
            return "Race"
        return self.name
