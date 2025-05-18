"""
Store all project constants here. NLTK would be perfect for entity extraction for Stage and Race Enums
but it is overkill and simple regex based string manipulation is used instead.
"""
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


# As a first approach, try to full match some F1 stages
# TODO: Maybe add sprint stages for a full solution
_stage_mapping = {
    r"fp1": Stage.FP1,
    r"free practice 1": Stage.FP1,
    r"practice 1": Stage.FP1,
    r"fp2": Stage.FP2,
    r"free practice 2": Stage.FP2,
    r"practice 2": Stage.FP2,
    r"fp3": Stage.FP3,
    r"free practice 3": Stage.FP3,
    r"practice 3": Stage.FP3,
    r"fp": Stage.FP3,  # In the case of just unqualified practice assume the last
    r"practice": Stage.FP3,
    r"free practice": Stage.FP3,

    r"q1": Stage.Q1,
    r"qualifying 1": Stage.Q1,
    r"q2": Stage.Q2,
    r"qualifying 2": Stage.Q2,
    r"q3": Stage.Q3,
    r"qualifying 3": Stage.Q3,
    r"q": Stage.Q3, # In the case of just unqualified qualifying stage assume the last
    r"qualifying": Stage.Q3,
    r"quali": Stage.Q3,

    r"race": Stage.RACE,
    r"grand prix": Stage.RACE,
    r"gp": Stage.RACE,
}


# TODO: NLTK would do this in less lines and handle fuzz logic
def parse_stage_input(user_input: str) -> Stage | None:
    """
    Parses user input string and maps it to a Stage Enum.
    Applies default rules for "practice" (FP3) and "qualifying" (Q3).
    Returns None if no valid stage is found.
    """
    normalized_input = user_input.lower().strip()

    # Check for exact matches first using the mapping keys as patterns
    for pattern, stage_enum in _stage_mapping.items():
        if re.fullmatch(pattern, normalized_input):
            return stage_enum
    
    # Try and match numbered stages for practice
    match_fp = re.fullmatch(r"(?:fp|free practice|practice)\s*([1-3])", normalized_input)
    if match_fp:
        num = match_fp.group(1)
        return getattr(Stage, f"FP{num}", None)

    # Try and match numbered stages for qualifying
    match_q = re.fullmatch(r"(?:q|qualifying|quali)\s*([1-3])", normalized_input)
    if match_q:
        num = match_q.group(1)
        return getattr(Stage, f"Q{num}", None)

    return None
