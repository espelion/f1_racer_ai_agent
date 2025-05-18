"""
Simulate some actions for the Racer.
"""
import logging

LOGGER = logging.getLogger(__name__)

class ActionSimulator:
    """
    Simulates social media actions.
    LOGGER config should be set to DEBUG level to see the noisy actions
    """
    def reply_to_comment(
            self, generated_reply_text: str, original_comment: str, 
            commenter: str = "Trixie"
            ):
        # TODO: If there was an actual replying API, the logic would go here
        LOGGER.debug(f"Action: Replying to {commenter}'s comment ('{original_comment}')")
        LOGGER.debug(f"Agent Reply: \"{generated_reply_text}\"")

    def post_status_update(self, generated_post_text: str):
        # TODO: If there was an actual posting API, the logic would go here
        LOGGER.debug(f"Action: Posting new status update:")
        LOGGER.debug(f"Agent Post: \"{generated_post_text}\"")

    def like_post(self, post_content: str, author: str = "Trixie"):
        # TODO: If there was an actual liking API, the logic would go here
        LOGGER.info(f'Action: Liking post from {author}: {post_content}')

    def mention_entity(self, entity_name: str, generated_text_with_mention: str):
        # TODO: If there was an actual mentioning API, the logic would go here
        LOGGER.debug(f"Action: Mentioning {entity_name} in a post.")
        LOGGER.debug(f"Agent Post with Mention: \"{generated_text_with_mention}\"")
