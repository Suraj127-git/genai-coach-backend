from fastapi.responses import PlainTextResponse

def metrics_response() -> PlainTextResponse:
    return PlainTextResponse(
        content="# HELP app_info Application information\n"
                "# TYPE app_info gauge\n"
                'app_info{version="0.1.0",service="genai-coach-backend"} 1\n'
    )

