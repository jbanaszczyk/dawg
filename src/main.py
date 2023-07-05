import logging

import typer

from src.custom_logging.setup_logging import setup_logging

app = typer.Typer()
logger = logging.getLogger("main")


@app.command()
def show_logs():
    logging.debug("logging: debug message")
    logging.info("logging: info message")
    logging.warning("logging: warn message")
    logging.error("logging: error message")
    logging.critical("logging: critical message")

    logger.debug("specific logger: debug message")
    logger.info("specific logger: info message")
    logger.warning("specific logger: warn message")
    logger.error("specific logger: error message")
    logger.critical("specific logger: critical message")


@app.command()
def hello(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    setup_logging()
    app()
