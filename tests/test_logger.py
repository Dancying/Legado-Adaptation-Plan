from utils.logger import get_logger


def test_log_message():
    logger = get_logger()
    logger.info("Info Message")
    logger.info("Info Message")
    logger.info("Info Message")
    logger.debug("Debug Message")
    logger.warning("Warning Message")
    logger.error("Error Message")
    logger.error("Error Message")
    logger.error("Error Message")


if __name__ == '__main__':
    test_log_message()
