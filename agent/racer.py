"""
Racer specific context
"""
from agent.actions import ActionSimulator
from agent.state import AgentState
from agent.text_generator import TextGenerator
from project.const import Result, Stage


class Racer:
    def __init__(self, text_generator: TextGenerator, racer_name: str, team_name: str):
        self.state = AgentState(racer_name, team_name)
        self.state.racer_name = racer_name
        self.state.team_name = team_name
        self.text_generator = text_generator
        self.action_simulator = ActionSimulator()

    def update_context_stage(self, new_stage: Stage):
        """
        Example stages: FP1, Q3, RACE.
        """
        self.state.update_stage(new_stage)

    def record_race_result(self, result: str):
        """
        Example results: 'P1', 'P5', 'DNF'.
        """
        self.state.record_result(result)

    def post_update(self, race_name: str):
        """
        Call post action.
        """
        context = self.state.get_context()
        context["race_name"] = race_name
        post_text = self.text_generator.generate_post(context)
        self.action_simulator.post_status_update(post_text)
        return post_text

    def reply_to_fan(self, fan_comment: str, race_name):
        """
        Call reply action.
        """
        context = self.state.get_context()
        context["race_name"] = race_name
        reply_text = self.text_generator.generate_reply(context, fan_comment)
        self.action_simulator.reply_to_comment(reply_text, fan_comment)
        return reply_text

    def like_post(self, post_content: str, author: str = "Trixie"):
        """
        Call like action.
        """
        self.action_simulator.like_post(post_content, author)

    def mention(self, entity_to_mention: str, race_name: str, base_message: str = "Great job!"):
        """
        A more advanced version would have the text_generator incorporate the mention naturally.
        For a simpler version, we can just append or use a template.
        """
        context = self.state.get_context()
        context["race_name"] = race_name
        if not entity_to_mention:
            entity_to_mention = "team"
        mention_text = self.text_generator.generate_mention_post(context, entity_to_mention, base_message)
        self.action_simulator.mention_entity(entity_to_mention, mention_text)
        return mention_text
