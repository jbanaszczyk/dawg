import atexit
import logging
import logging.config
import os
import os.path
from importlib import resources
from typing import Optional, Any, List, Tuple

import coloredlogs
import yaml

_nameToLevel = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}


def _safe_str_to_int(value: Any) -> Optional[int]:
    try:
        if value.isnumeric():
            return int(value)
    except (ValueError, AttributeError):
        pass
    return None


def _yaml_safe_load_or_none(config_data):
    if config_data:
        try:
            return yaml.safe_load(config_data)
        except yaml.YAMLError:
            pass


def _read_config_from_resources(config_filename, trace: List[Tuple[int, str]]):
    try:
        config = resources.files(__package__).joinpath(config_filename).read_text(encoding="UTF-8")
        trace.append((logging.DEBUG, f"config from resource: {config_filename}"))
        return config
    except (OSError, ValueError):
        return None


def _read_config_from_filesystem(config_filename, trace: List[Tuple[int, str]]):
    try:
        with open(config_filename, "rt", encoding="UTF-8") as f:
            config = f.read()
        trace.append((logging.DEBUG, f"config from file: {config_filename}"))
        return config
    except (OSError, ValueError):
        return None


def _post_mortem(trace):
    for event_level, event_message in trace:
        logging.log(event_level, f"setup_logging: {event_message}")


# noinspection PyBroadException
def setup_logging(default_config_filename: str = "logging.yaml", default_level: int = None, env_key_log_level: str = "LOG_LEVEL", env_key_log_config: str = "LOG_CONFIG") -> None:
    post_mortem_trace: List[Tuple[int, str]] = []
    atexit.register(_post_mortem, post_mortem_trace)

    post_mortem_trace.append((logging.DEBUG, f"looking for env. variable {env_key_log_level}"))
    forced_log_level: Optional[str] = os.getenv(env_key_log_level, None)

    log_level = _safe_str_to_int(forced_log_level)

    if not log_level:
        if isinstance(forced_log_level, str):
            forced_log_level = forced_log_level.upper()
        if forced_log_level:
            log_level = _nameToLevel.get(forced_log_level, logging.INFO)

    if not log_level:
        log_level = default_level

    post_mortem_trace.append((logging.DEBUG, f"looking for env. variable {env_key_log_config}"))
    config_filename = os.getenv(env_key_log_config, None) or default_config_filename

    config_data = _read_config_from_resources(config_filename, post_mortem_trace) or _read_config_from_filesystem(config_filename, post_mortem_trace)
    config = _yaml_safe_load_or_none(config_data)

    if config:

        if log_level:
            for logger in config["loggers"]:
                config["loggers"][logger]["level"] = log_level

        try:
            for handler in config["handlers"]:
                log_file_name = config["handlers"][handler].get("filename", None)
                if log_file_name:
                    log_directory = os.path.dirname(log_file_name)
                    if not os.path.isdir(log_directory):
                        post_mortem_trace.append((logging.INFO, f"creating directory {log_directory}"))
                        os.makedirs(log_directory, exist_ok=True)
        except OSError as e:
            post_mortem_trace.append((logging.ERROR, str(e)))
            config = None

    if config:
        try:
            logging.config.dictConfig(config)
        except ValueError as e:
            post_mortem_trace.append((logging.ERROR, str(e)))
            config = None

    if not config:
        logging.basicConfig(level=log_level)
        coloredlogs.install(level=log_level)
        post_mortem_trace.append((log_level if log_level else logging.WARNING, f"using defaults"))

    atexit.unregister(_post_mortem)
    _post_mortem(post_mortem_trace)
