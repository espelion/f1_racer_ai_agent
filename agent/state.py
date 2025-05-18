"""
Maintain the agent's state
"""
import logging
from typing import Optional

from project.const import Stage, Result


LOGGER = logging.getLogger(__name__)

class AgentState:
    """
    Manages the agent's contextual awareness. For a multi-dimensional character, this where 
    entities like mood team morale could be defined
    """
    def __init__(self, racer_name: str, team_name: str, current_stage: Stage = Stage.FP1):
        self.current_stage: Stage = current_stage
        self.last_result: Optional[Result] = None
        self.team_name: str = team_name
        self.racer_name: str = racer_name

    def update_stage(self, new_stage: Stage):
        """
        Updates the agent's current stage.
        """
        self.current_stage = new_stage
        LOGGER.debug(f"Agent context updated: Current stage is now {new_stage.value} ({new_stage.name})")

    def record_result(self, result: str):
        """
        Records the race result after parsing it.
        """
        parsed_result = Result.from_string(result)
        if parsed_result:
            self.last_result = parsed_result
            LOGGER.debug(f"Race result recorded: {self.last_result}")
        else:
            # Warn the user if the result is not updated. Optionally raise an error
            LOGGER.warning(f"Could not parse race result: '{result}'. Result not updated.")

    def get_context(self):
        """
        Return current context.
        """
        return {
            "stage": self.current_stage,
            "result": self.last_result,
            "team_name": self.team_name,
            "racer_name": self.racer_name,
        }
