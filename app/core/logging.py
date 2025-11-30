import logging

def configure_logging(service: str = "genai-coach-backend") -> None:
    handler = logging.StreamHandler()
    fmt = f'{{"t":"%(asctime)s","lvl":"%(levelname)s","logger":"%(name)s","msg":"%(message)s","service":"{service}"}}'
    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%dT%H:%M:%S")
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = []
    root.setLevel(logging.INFO)
    root.addHandler(handler)
