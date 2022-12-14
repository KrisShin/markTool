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
    for work_name in read_file('WORKS'):
        work_list.append(f'<li><a href="/{work_name}">{work_name}</a></li>')

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
    (
        work_mapping,
        value_max_score,
        value_min_score,
        value_score_step,
    ) = read_file(['WORKS', 'value_max_score', 'value_min_score', 'value_score_step'])

    file_info = work_mapping.get(filename)
    if not file_info:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    uri = f'{BASE_URL}/{SERVER_STATICFOLDER}/{filename}'

    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    media_html = f'<h2> {filename} </h2>'
    if ext in IMAGE_EXTS:
        media_html = f'<img src="{uri}" alt="{filename}" width=480></img>'
    elif ext in VIDEO_EXTS:
        media_html = f'''
        <video alt="{filename}" width=480 controls autoplay>
            <source src="{uri}" type="video/mp4">
            Your browser does not support the video tag.
        </video>'''
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
                <input type="number" name="score" min="{value_min_score}" max="{value_max_score}" step="{value_score_step}" required/>
                <button type="submit">submit</button>
            </form>
        </body>
    </html>
    """


@app.post("/{filename}/", response_class=HTMLResponse)
def post_score(filename, request: Request, score: float = Form()):
    print(filename, score)
    _check_server_allowed()
    (
        work_mapping,
        value_max_score,
        value_min_score,
        value_score_step,
    ) = read_file(['WORKS', 'value_max_score', 'value_min_score', 'value_score_step'])

    value_max_score = float(value_max_score)
    value_min_score = float(value_min_score)
    value_score_step = float(value_score_step)
    file_info = work_mapping.get(filename)

    if not file_info:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not all((value_max_score > 0, value_min_score >= 0, value_score_step > 0)):
        return f"""
                <html>
                    <head>
                        <title>Mark Tool - {filename}</title>
                    </head>
                    <body>
                        <h3> Wrong config, Please contact administrator. </h3>
                        <h3> Please re-grade. </h3>
                        <h2>return <a href="/works/">work list</a></h2>
                    </body>
                </html>
                """
    if any((score < value_min_score, score > value_max_score)):
        return f"""
                <html>
                    <head>
                        <title>Mark Tool - {filename}</title>
                    </head>
                    <body>
                        <h3> Score must between {value_min_score} and {value_max_score} </h3>
                        <h3> Please re-grade. </h3>
                        <h2>return <a href="/works/">work list</a></h2>
                    </body>
                </html>
                """

    if (score - value_min_score) / value_score_step % 1 != 0:
        score = value_min_score + (
            (score - value_min_score) // value_score_step * value_score_step
        )
    ip_address = request.client.host
    scores = file_info.get('scores', {})
    if ip_address in scores:
        return f"""
                <html>
                    <head>
                        <title>Mark Tool - {filename}</title>
                    </head>
                    <body>
                        <h3> You have already graded. </h3>
                        <h3> Thank you. </h3>
                        <h2>return <a href="/works/">work list</a></h2>
                    </body>
                </html>
                """
    scores.update({ip_address: score})
    file_info.update({'scores': scores})
    save_file({'WORKS': work_mapping})
    save_file({'status_msg': f'{ip_address} grade {score} to {filename}'})

    return f"""
    <html>
        <head>
            <title>Mark Tool - {filename}</title>
        </head>
        <body>
            <h3> {filename} get {score} </h3>
            <h3> Thank you. </h3>
            <h2>return <a href="/works/">work list</a></h2>
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
        for work_name, work_dict in WORKS.items():
            if work_name in current_files:
                continue
            shutil.copy(
                work_dict['uri'],
                f'./{SERVER_STATICFOLDER}/{work_name}',
            )
        app.mount("/static", StaticFiles(directory="static"), name="static")
        # TODO create static folder if not exist. and copy file to static directory.
        uvicorn.run(app, host='0.0.0.0', port=SERVER_PORT, log_level="info")


if __name__ == "__main__":
    # testy_server = uvicorn.run(app, port=SERVER_PORT, log_level="info")
    # testy_server.shutdown()
    ...
