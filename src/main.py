import datetime as dt
import pathlib
from functools import partial
from urllib.parse import urljoin
from uuid import uuid4

import aiosqlite
import uvicorn
from starlette.applications import Starlette
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from _migrations import setup_tables, setup_default_account
from config import load_config, Config
from utils import convert_to_webp, save_file, filename_without_ext


async def cloudflare_direct_upload(request: Request):
    image_id = str(uuid4())

    await server.state.db_connection.execute('''
        INSERT INTO image(image_id, name, uploaded_at, require_signed_urls, draft, account_id) VALUES(?, ?, ?, ?, ?, ?);
    ''', (image_id, None, int(dt.datetime.now().timestamp()), False, True, request.path_params['account_id']))
    await server.state.db_connection.commit()

    return JSONResponse({
        'errors': [],
        'messages': [],
        'result': {
            'id': image_id,
            'uploadURL': urljoin(server.state.config.hostname, f'/cloudflare/{image_id}'),
        }
    })


async def cloudflare_upload_image(request: Request):
    form = await request.form()
    file = form.get('file')
    file_path = pathlib.Path(server.state.config.images_storage) / file.filename
    file_content = await file.read()

    db = server.state.db_connection

    cursor = await db.execute(f'SELECT * FROM image WHERE image_id = ? AND draft = ?', (str(request.path_params['image_id']), True))
    if await cursor.fetchone() is None:
        return Response(status_code=404)

    tasks = BackgroundTasks()
    tasks.add_task(save_file, file_path, file_content)
    tasks.add_task(convert_to_webp, file_path)

    await db.execute(f'UPDATE image SET draft = 0, name = ? WHERE image_id = ?', (filename_without_ext(file.filename), str(request.path_params['image_id'])))
    await db.commit()

    return JSONResponse({'status': 'ok'}, background=tasks)


async def cloudflare_get_image(request: Request):
    account_id = request.path_params['account_id']
    image_id = str(request.path_params['image_id'])
    db = server.state.db_connection

    cursor = await db.execute('SELECT name FROM image WHERE image_id = ? AND account_id = ? AND draft = ?', (image_id, account_id, False))
    result = await cursor.fetchone()
    if result:
        f = open(str(pathlib.Path(server.state.config.images_storage) / result[0]) + '.webp', 'rb')
        return Response(
            content=f.read(),
            headers={
                'content-type': 'image/webp'
            }
        )


async def startup(cfg: Config):
    db = '_internalstate/cloudflare.db' if config.persistence else ':memory:'
    server.state.db_connection = await aiosqlite.connect(db)

    server.state.config = cfg

    await setup_tables(server.state.db_connection)
    await setup_default_account(cfg, server.state.db_connection)


async def shutdown() -> None:
    await server.state.db_connection.close()


server_routes = [
    # cloudflare urls:
    Route('/cloudflare/client/v4/accounts/{account_id:str}/images/v2/direct_upload', cloudflare_direct_upload,
          methods=['POST']),
    Route('/cloudflare/{image_id:uuid}', cloudflare_upload_image, methods=['POST']),
    Route('/cloudflare/{account_id:str}/{image_id:uuid}/{variant:str}', cloudflare_get_image, methods=['GET']),
    # ...
]

config = load_config()
server = Starlette(
    debug=config.debug,
    routes=server_routes,
    on_startup=[partial(startup, config)],
    on_shutdown=[shutdown],
)
if __name__ == '__main__':
    uvicorn.run('main:server', port=8000, host='0.0.0.0')
