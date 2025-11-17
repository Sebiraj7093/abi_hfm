import os

from hf_logger.factory import HfLoggerFactory
from hf_logger.manager import HfLoggerManager

from configuration import APPLICATION_NAME
from configuration import CONFIG_DIR


def init_logger():
    params = dict(
        app_name=APPLICATION_NAME,
        config_path=os.path.join(CONFIG_DIR, "logging/log_config.yaml"),
    )
    hf_logger = HfLoggerFactory(**params)
    hf_logger("AppLogger")

    return HfLoggerManager(hf_logger)


logger = init_logger()
