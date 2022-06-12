import sys
import logging
import json_logging
from fastapi import FastAPI
from fastapi_utils.timing import add_timing_middleware


def configure_logger(logger: logging.Logger, app: FastAPI) -> None:
    """ Configuring Logger to set the logging level, handlers and JSON formatter.
    Args
    ----
        logger (logging.Logger): Logger to configure.
        app (FastAPI): FastAPI application to use.

    Returns
    -------
        None
    """
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    json_logging.init_fastapi(enable_json=True)
    json_logging.init_request_instrument(app)

    add_timing_middleware(app, record=logger.info, prefix="app")

