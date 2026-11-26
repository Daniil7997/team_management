# import logging
# import sys

# from pythonjsonlogger.json import JsonFormatter


# def setup_logging() -> None:
#     formatter = JsonFormatter(
#         "%(asctime)s %(levelname)s %(name)s %(message)s "
#         "%(client_addr)s %(method)s %(path)s "
#         "%(http_version)s %(status_code)s",
#         rename_fields={
#             "asctime": "timestamp",
#             "levelname": "level",
#             "name": "logger",
#         },
#     )

#     handler = logging.StreamHandler(sys.stdout)
#     handler.setFormatter(formatter)

#     root_logger = logging.getLogger()
#     root_logger.setLevel(logging.INFO)

#     root_logger.handlers.clear()
#     root_logger.addHandler(handler)

#     # Uvicorn
#     uvicorn_loggers = {
#         "uvicorn",
#         "uvicorn.error",
#         "uvicorn.access",
#     }

#     for logger_name in uvicorn_loggers:
#         uvicorn_logger = logging.getLogger(logger_name)
#         uvicorn_logger.handlers.clear()
#         uvicorn_logger.addHandler(handler)
#         uvicorn_logger.propagate = False
