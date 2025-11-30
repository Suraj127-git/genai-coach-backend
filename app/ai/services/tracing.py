import os

def configure_langsmith(api_key: str | None, enable: bool) -> None:
    if api_key and enable:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = api_key
