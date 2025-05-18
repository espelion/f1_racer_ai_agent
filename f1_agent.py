import argparse
import logging

from agent.racer import Racer
from agent.text_generator import GeminiTextGenerator, TemplateBasedTextGenerator, TextGenerator, TransformerTextGenerator
from project.const import parse_stage_input
from project.logger import setup_logging

setup_logging()
LOGGER = logging.getLogger(__name__)

def print_help():
    """Prints the available commands for the interactive loop."""
    print("\nAvailable commands:")
    print("  help                          - Show this help message.")
    print("  quit / q                      - Exit the interactive mode.")
    print("  state                         - Show current agent state and race name.")
    print("  stage <new_stage>             - Update agent's current race stage (Example: FP1, Q2, Race).")
    print("  result <new_result>           - Record agent's last race result (Example: P1, P5, DNF).")
    print("  racename <new_race_name>      - Set the current race name (Example MonzaGP).")
    print("  post                          - Agent generates and 'posts' a status update based on current context.")
    print("  reply <fan_comment_text>      - Agent generates a 'reply' to the given fan comment.")
    print("  mention <entity> [message]    - Agent 'posts' mentioning an entity. Message is optional (defaults to 'Great job by {mention}!').")
    print("                                  Example: mention MyMechanic")
    print("                                  Example: mention Sponsor Great race thanks to {mention}!")
    print("  like <post_content> [author]  - Agent 'likes' a post. Author is optional (defaults to 'Trixie').")
    print("                                  Example: like \"Well done team\"")
    print("                                  Example: like \"Good fight\" Max")
    print("\n")

def interactive_loop(agent: Racer):
    """Runs an interactive command loop to control the Racer."""
    LOGGER.info("F1 Racer Agent Interactive Mode. Type 'help' for commands, 'quit' to exit.")
    current_race_name = "SilverstoneGP"
    print_help()

    while True:
        try:
            prompt = f"({agent.state.current_stage.name if agent.state.current_stage else 'N/A Stage'}, Res: {agent.state.last_result or 'N/A'}, Race: {current_race_name}) > "
            raw_input_str = input(prompt).strip()

            if not raw_input_str:
                continue

            command_parts = raw_input_str.split(" ", 1)
            command = command_parts[0].lower()
            args_str = command_parts[1] if len(command_parts) > 1 else ""

            if command in ["quit", "q"]:
                LOGGER.info("Exiting interactive mode.")
                break
            elif command == "help":
                print_help()
            elif command == "state":
                print(f"  Current Stage: {agent.state.current_stage.value if agent.state.current_stage else 'Not set'} ({agent.state.current_stage.name if agent.state.current_stage else 'N/A'})")
                last_result_str = str(agent.state.last_result) if agent.state.last_result else 'N/A'
                print(f"  Last Result:   {last_result_str}")
                print(f"  Racer Name:    {agent.state.racer_name}")
                print(f"  Team Name:     {agent.state.team_name}")
                print(f"  Current Race:  {current_race_name}")
            elif command == "stage":
                if args_str:
                    parsed_stage = parse_stage_input(args_str)
                    if parsed_stage:
                        agent.update_context_stage(parsed_stage)
                    else:
                        LOGGER.warning(f"Invalid stage input: '{args_str}'. Please use formats like FP1, Q2, Race, Practice, Qualifying.")
                else:
                    LOGGER.warning("Usage: stage <new_stage>")
            elif command == "result":
                if args_str:
                    agent.record_race_result(args_str)
                else:
                    LOGGER.warning("Usage: result <new_result>")
            elif command == "racename":
                if args_str:
                    current_race_name = args_str
                    LOGGER.info(f"Current race name set to: {current_race_name}")
                else:
                    LOGGER.warning("Usage: racename <new_race_name>")
            elif command == "post":
                post_text = agent.post_update(race_name=current_race_name)
                print(f"Agent posted: {post_text}")
            elif command == "reply":
                if args_str:
                    reply_text = agent.reply_to_fan(fan_comment=args_str, race_name=current_race_name)
                    print(f"Agent replied: {reply_text}")
                else:
                    LOGGER.warning("Usage: reply <fan_comment_text>")
            elif command == "mention":
                mention_args = args_str.split(" ", 1)
                entity = mention_args[0] if mention_args else "team"
                message = mention_args[1] if len(mention_args) > 1 else "Great job by {mention}!"
                if entity:
                    post_text = agent.mention(entity_to_mention=entity, base_message=message, race_name=current_race_name)
                    print(f'Agent posted with mention: {post_text}')
                else:
                    LOGGER.warning("Usage: mention <entity_to_mention> [base_message]")
            elif command == "like":
                like_args = args_str.split('" ', 1)
                content = f'{like_args[0]}"' if like_args else ""
                author = like_args[1] if len(like_args) > 1 else None
                if content:
                    if author:
                        agent.like_post(post_content=content, author=author)
                    else:
                        agent.like_post(post_content=content)
                else:
                    LOGGER.warning("Usage: like <post_content> [author]")
            else:
                LOGGER.warning(f"Unknown command: {command}. Type 'help' for available commands.")

        except EOFError:
            LOGGER.info("\nExiting interactive mode (EOF).")
            break
        except KeyboardInterrupt:
            LOGGER.info("\nExiting interactive mode (Interrupt).")
            break
        except Exception as e:
            LOGGER.error(f"An error occurred in the loop: {e}", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the F1 Racer AI Agent.")
    parser.add_argument(
        "--text-generator",
        type=str,
        choices=["basic", "gemini", "transformer"],
        default="basic",
        help="Specify the text generator: 'basic' (template), 'gemini' "
        "(Google Gemini). Default: 'basic'."
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="distilgpt2",
        help="Specify the Hugging Face model name to use if"
         " --text-generator is 'transformer'. Default is 'distilgpt2'."
    )
    args = parser.parse_args()

    text_gen: TextGenerator
    if args.text_generator == "transformer":
        LOGGER.info(f"Using TransformerTextGenerator with model: {args.model_name}")
        text_gen = TransformerTextGenerator(model_name=args.model_name)
    elif args.text_generator == "gemini":
        LOGGER.info("Using GeminiTextGenerator.")
        text_gen = GeminiTextGenerator()
    else:
        LOGGER.info("Using TemplateBasedTextGenerator.")
        text_gen = TemplateBasedTextGenerator()

    agent = Racer(text_generator=text_gen, racer_name="Go Mifune", team_name="Mach 5")

    interactive_loop(agent)
