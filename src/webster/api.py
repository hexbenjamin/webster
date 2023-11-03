import sys

import g4f
from g4f.api import Api
from loguru import logger


def run_api() -> None:
    """
    Run the G4F API interference server.
    """
    logger.disable("g4f")
    Api(engine=g4f, debug=False).run(
        bind_str="127.0.0.1:1337" if sys.platform == "win32" else "0.0.0.0:1337"
    )


if __name__ == "__main__":
    run_api()
