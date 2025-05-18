"""
Separate file for a sigleton logger across the project.
"""
import json
import logging
import pathlib
from logging import config

def setup_basic_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} {levelname} {name}:{lineno} {message}",
        datefmt="%Y-%m-%dT%H:%M:%S", style="{"
    )



# Get the root logger, necessary for the initial logging while project logger is being set up
LOGGER = logging.getLogger()


def setup_logging():
    # Construct the path to logger.json, assuming it's in the parent directory of 
    # the 'project' directory
    config_file_path = pathlib.Path(__file__).resolve().parent.parent / "logger.json"
    try:
        with open(config_file_path) as f:
            logging_config = json.load(f)
    except FileNotFoundError as e:
        LOGGER.exception(e)
        # Use a basic logger if logger.json is not found
        setup_basic_logging()
        LOGGER.info("Running with the basic config")
    else:
        try:
            # Otherwise set up a logger using the dict config method
            config.dictConfig(logging_config)
        except (TypeError, ValueError) as e:
            LOGGER.exception(e)
            setup_basic_logging()
            LOGGER.info("Running with the basic config")
        else:
            LOGGER.info(f"Running with the log config at {config_file_path}")
