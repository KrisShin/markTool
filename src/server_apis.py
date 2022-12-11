from http.client import HTTPException
import re
from src.settings import SERVER_ALLOWED, SERVER_PORT, WORKS
import requests
import uvicorn
from fastapi import FastAPI, status, HTTPException
from fastapi.exceptions import FastAPIError
from fastapi.responses import HTMLResponse

app = FastAPI()


def _check_server_allowed():
    if not SERVER_ALLOWED:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/test_server/")
def test_server():
    _check_server_allowed()
    print('test server success.')
    return True


@app.get("/works/", response_class=HTMLResponse)
def get_works():
    _check_server_allowed()

    works_name_html_str = WORKS
    return f"""
    <html>
        <head>
            <title>Mark Tool - works list</title>
        </head>
        <body>
            {works_name_html_str}
        </body>
    </html>
    """


class WebServerManager:
    @classmethod
    def test_server(cls) -> int:
        resp = requests.get(f'http://localhost:{SERVER_PORT}/test_server/')
        return resp.status_code

    @classmethod
    def launch_server(cls):
        uvicorn.run(app, host='0.0.0.0', port=SERVER_PORT, log_level="info")


if __name__ == "__main__":
    testy_server = uvicorn.run(app, port=SERVER_PORT, log_level="info")
    print('fuck')
    testy_server.shutdown()
