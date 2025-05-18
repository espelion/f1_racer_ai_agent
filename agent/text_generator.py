"""
Text generators as Interfaces/Abstract Base Class
"""
import logging
import random
import os
from abc import ABC, abstractmethod

from agent.utils import sentiment_analysis
from project.const import Stage, TEMPLATES, Result


LOGGER = logging.getLogger(__name__)

# TODO: Maybe a Protocol to keep up with the times
class TextGenerator(ABC):
    @abstractmethod
    def generate_post(self, context: dict) -> str:
        pass

    @abstractmethod
    def generate_reply(self, context: dict, original_comment: str) -> str:
        pass
    
    @abstractmethod
    def generate_mention_post(self, context: dict, entity_to_mention: str, base_message: str) -> str:
        pass


class TemplateBasedTextGenerator(TextGenerator):
    """
    Generates text using predefined templates and racer vocabulary. Uses a sentiment analysis for replies
    """
    def __init__(self):
        self.templates = TEMPLATES

    def _get_race_name_placeholder(self, context: dict):
        return context.get("race_name", "SilverstoneGP")

    def _get_stage_abbr(self, stage: Stage):
        return stage.short_name

    def generate_post(self, context: dict) -> str:
        stage = context.get("stage", Stage.FP1)
        result: Result | None = context.get("result")
        team_name = context.get("team_name", "Mach 5")
        race_name = self._get_race_name_placeholder(context)
        stage_abbr = self._get_stage_abbr(stage)

        # Set up default context before calculating it
        key = "practice_1"
        result_detail_for_quali = str(result) if result else "a good spot"
        suffix = ""

        # Use result and stage to set up the right template
        if result:
            if result == Result.P1:
                suffix = "_win"
            elif result in [Result.P2, Result.P3, Result.P4, Result.P5, Result.TOP_3, Result.TOP_5]:
                suffix = "_good_result"
            elif result == Result.DNF:
                suffix = "_dnf"
            elif result in [getattr(Result, f"P{i}") for i in range(6, 21)]:
                suffix = "_difficult_race"
            else:
                suffix = "_difficult_race"

        # If it was a race then we do not need extra placing context, just result
        if stage == Stage.RACE and suffix:
            key = suffix[1:] # Remove underscore
        # If it was qualifying then we need extra placing context
        elif stage in [Stage.Q1, Stage.Q2, Stage.Q3]:
            if stage == Stage.Q1:
                key = f"qualifying_1{suffix}"
            elif stage == Stage.Q2: #
                key = f"qualifying_2{suffix}"
            else:
                key = f"qualifying_3{suffix}"
            if result:
                result_detail_for_quali = result
        # If it was practice then we need extra placing context
        elif stage in [Stage.FP1, Stage.FP2, Stage.FP3]:
            if stage == Stage.FP1:
                key = f"practice_1{suffix}"
            elif stage == Stage.FP2:
                key = f"practice_2{suffix}"
            else:
                key = f"practice_3{suffix}"
        # Not necessary but elif's look better with an else clause
        else:
            key = "practice_1"
        LOGGER.debug(f"Calling template - {key}")
        template_list = self.templates.get(key, self.templates["practice_1"])
        chosen_template = random.choice(template_list)
        
        # Inject context using string formating
        return chosen_template.format(
            team_name=team_name,
            race_name=race_name,
            stage=stage.value,
            stage_abbr=stage_abbr,
            result_detail=result_detail_for_quali
        )

    def generate_reply(self, context: dict, original_comment: str) -> str:
        racer_name = context.get("racer_name", "I")
        compound_score = sentiment_analysis(original_comment)

        LOGGER.debug(f"Fan comment: '{original_comment}', Sentiment (compound): {compound_score}")

        if compound_score >= 0.05:
            reply_list = self.templates["reply_positive"]
        elif compound_score <= -0.05:
            reply_list = self.templates["reply_negative"]
        elif compound_score is None:
            # Fallback if NLTK/VADER is not available
            reply_list = self.templates["reply_neutral"]
        else:
            reply_list = self.templates["reply_neutral"]
    

        return f"{racer_name} replies: {random.choice(reply_list)}"

    def generate_mention_post(self, context: dict, entity_to_mention: str, base_message: str) -> str:
        compound_score = sentiment_analysis(base_message)
        if compound_score >= 0.05:
            message = f"{base_message}, Big shoutout to @{entity_to_mention}!"
        elif compound_score <= -0.05:
            message = f"{base_message} But still a huge shoutout to @{entity_to_mention}!"
        else:
            # Fallback if NLTK/VADER is not available or neutral
            message = f"{base_message} Shoutout to @{entity_to_mention}!"
        
        if context["stage"] == Stage.RACE and context["result"] == Result.P1:
            message += f" #Team{context['team_name']} #Winner"

        return message
