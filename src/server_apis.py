from http.client import HTTPException
import os
import shutil
import requests
import uvicorn
from fastapi import FastAPI, status, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.settings import (
    BASE_URL,
    IMAGE_EXTS,
    SERVER_PORT,
    SERVER_STATICFOLDER,
    TEXT_EXTS,
    VIDEO_EXTS,
)

from src.utils import read_file, save_file

app = FastAPI()


def _check_server_allowed():
    SERVER_ALLOWED = read_file('SERVER_ALLOED')
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
    work_list = []
    for work in read_file('WORKS'):
        for name in work:
            work_list.append(f'<li><a href="/{name}">{name}</a></li>')

    return f"""
    <html>
        <head>
            <title>Mark Tool - works list</title>
        </head>
        <body>
            <h3> mark the works </h3>
            <ul>
                {''.join(work_list)}
            </ul>
        </body>
    </html>
    """


@app.get("/{filename}/", response_class=HTMLResponse)
def get_file(filename):
    _check_server_allowed()
    work_mapping = {}
    for work in read_file('WORKS'):
        work_mapping.update(work)
    file_info = work_mapping.get(filename)
    if not file_info:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    uri = f'{BASE_URL}/{SERVER_STATICFOLDER}/{filename}'

    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    media_html = f'<h2> {filename} </h2>'
    if ext in IMAGE_EXTS:
        media_html = f'<img src="{uri}" alt="{filename}"></img>'
    elif ext in VIDEO_EXTS:
        media_html = f'<video src="{uri}" alt="{filename}" controls autoplay></video>'
    elif ext in TEXT_EXTS:
        content
        with open(uri, 'r') as fp:
            content = fp.read()
        media_html = f'<p>{content}</p>'

    return f"""
    <html>
        <head>
            <title>Mark Tool - {filename}</title>
        </head>
        <body>
            <h3> {filename} </h3>
            {media_html}
            <form action="/{filename}/" method="post">
                <input type="number" name="score">
                <button type="submit">submit</button>
            </form>
        </body>
    </html>
    """


@app.post("/{filename}/", response_class=HTMLResponse)
def post_score(filename, score: float = Form()):
    _check_server_allowed()
    (
        works,
        value_max_score,
        value_min_score,
        value_score_step,
    ) = read_file(['WORKS', 'value_max_score', 'value_min_score', 'value_score_step'])
    work_mapping = {}
    for work in works:
        work_mapping.update(work)

    value_max_score = float(value_max_score)
    value_min_score = float(value_min_score)
    value_score_step = float(value_score_step)
    file_info = work_mapping.get(filename)
    if not file_info:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not all((value_max_score > 0, value_min_score >= 0, value_score_step > 0)):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='config error'
        )
    if any((score < value_min_score or score > value_max_score)):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='score error'
        )

    if (score - value_min_score) / value_score_step % 1 != 0:
        score = value_min_score + (
            (score - value_min_score) // value_score_step * value_score_step
        )
    file_info.update({'scores': {'ip': request.client.host, 'score': score}})
    print(f'{request.client.host} mark {filename} {score}.')
    save_file({'WORKS': work_mapping})

    return f"""
    <html>
        <head>
            <title>Mark Tool - {filename}</title>
        </head>
        <body>
            <h3> {filename} get {score} </h3>
            <h3> Thank you. </h3>
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
        WORKS = read_file('WORKS')
        if not os.path.exists(SERVER_STATICFOLDER):
            os.mkdir(f'./{SERVER_STATICFOLDER}')

        current_files = os.listdir(f'./{SERVER_STATICFOLDER}')
        for work_dict in WORKS:
            for work_name in work_dict:
                if work_name in current_files:
                    continue
                shutil.copy(
                    work_dict[work_name]['uri'],
                    f'./{SERVER_STATICFOLDER}/{work_name}',
                )
        app.mount("/static", StaticFiles(directory="static"), name="static")
        # TODO create static folder if not exist. and copy file to static directory.
        uvicorn.run(app, host='0.0.0.0', port=SERVER_PORT, log_level="info")


if __name__ == "__main__":
    # testy_server = uvicorn.run(app, port=SERVER_PORT, log_level="info")
    # testy_server.shutdown()
    ...
