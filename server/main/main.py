import asyncio
import hashlib
import io
import os
import re
import time
from datetime import datetime
from multiprocessing.pool import ThreadPool

import fastapi
import requests
import uvicorn as uvicorn
import win32com.client
from aspose import slides
from fastapi import Cookie
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, HTMLResponse, FileResponse
from starlette.staticfiles import StaticFiles

from database.db_handler import DatabaseHandler, Users, Presentations, Slides, Tags, Links
from definitions import ROOT
from models.json_models import BuildPresentationModel
from utils import utils

origin = "http://localhost:8000"
# origin = "https://pres-configurator.ru"

SROOT = os.path.join(ROOT, 'server/main')

app = fastapi.FastAPI()
app.mount('/views', StaticFiles(directory=os.path.join(ROOT, 'client/views')), name="views")



origins = [
    origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_session = {}
db_handler = DatabaseHandler()
db_handler.create_db()

thread_pool = ThreadPool(processes=20)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@app.get('/auth/login')
def auth():
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    default_auth_flow = Flow.from_client_secrets_file(
        'auth/oauth2.keys.json',
        scopes=['openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/drive.file'
                ],
        redirect_uri=origin + '/auth/sessions'
    )
    user_session[state] = [None, default_auth_flow]
    auth_url, _ = default_auth_flow.authorization_url(
        access_type='offline',
        state=state
    )
    return RedirectResponse(url=auth_url)


@app.get('/auth/sessions')
def sessions(code, state):
    _, user_flow = user_session[state]
    user_flow.fetch_token(code=code)

    response = RedirectResponse(url="/")
    response.set_cookie(key="pres_conf_user_state", value=state)

    return response


@app.get('/')
def root(pres_conf_user_state: str = Cookie(default=None)):
    if pres_conf_user_state is None or user_session.get(pres_conf_user_state) is None:
        return RedirectResponse(url="/auth/login")

    _, user_flow = user_session[pres_conf_user_state]

    user_info_service = build('oauth2', 'v2', credentials=user_flow.credentials)
    user_info = user_info_service.userinfo().get().execute()

    user_id = user_info['id']
    user_name = user_info['name']

    db_handler.create(Users, id=user_id, name=user_name)

    user_session[pres_conf_user_state] = [user_id, user_flow]

    with open(os.path.join(ROOT, 'client/views/index.html'), encoding='utf-8') as fh:
        data = fh.read()
    return HTMLResponse(content=data)


@app.get('/auth/user-info')
def user_picture(pres_conf_user_state: str = Cookie(default=None)):
    _, user_flow = user_session[pres_conf_user_state]

    user_info_service = build('oauth2', 'v2', credentials=user_flow.credentials)
    user_info = user_info_service.userinfo().get().execute()

    user_name = user_info['name']
    picture_url = user_info['picture']

    return user_name, picture_url


# Возвращает список презентаций пользователя в виде дерева
# *Корней может быть несколько (Мой диск, а также папки, которыми поделились с пользователем)
@app.get('/presentations/tree')
def pres_tree(pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = user_session[pres_conf_user_state]
    presentations = pres_list(pres_conf_user_state)
    drive_service = build('drive', 'v3', credentials=user_flow.credentials)
    traversed = {}
    root_nodes = []
    for pres in presentations:
        node = {
            'type': 'pres',
            **pres
        }
        [parent] = pres.get('parents')
        while True:
            if parent not in traversed:
                parent_node = drive_service.files().get(
                    fileId=parent,
                    fields='id, name, parents').execute()
                if parent_node.get('parents') is None:
                    root_node = {
                        'type': 'root',
                        **parent_node,
                        'children': [node]
                    }
                    root_nodes.append(root_node)
                    traversed[parent_node.get('id')] = root_node
                    break
                else:
                    node = {
                        'type': 'folder',
                        **parent_node,
                        'children': [node]
                    }
                    traversed[node.get('id')] = node
                    [parent] = node.get('parents')
            else:
                traversed[parent]['children'].append(node)
                break

    return root_nodes


# Возвращает список pptx-презентаций пользователя в формате:
#  [
#   { id, name, modifiedTime, parents },
#   ...
#  ]
def pres_list(user_state):
    user_id, user_flow = user_session[user_state]
    drive_service = build('drive', 'v3', credentials=user_flow.credentials)
    response = drive_service.files().list(
        q="mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation' " \
          "and trashed = false",
        fields='files(id, name, modifiedTime, parents)').execute()
    presentations = [{**pres, 'owner_id': user_id} for pres in response.get('files')]
    return presentations


sync_status = {}


@app.post('/presentations/sync')
def pres_sync(pres_conf_user_state: str = Cookie(default=None)):

    user_id, user_flow = user_session[pres_conf_user_state]
    actual_pres_list = pres_list(pres_conf_user_state)
    db_pres_list = [pres.__dict__ for pres in db_handler.findall(Presentations, Presentations.owner_id == user_id)]
    not_changed, updated, created, removed = pres_list_delta(actual_pres_list, db_pres_list)
    print(f"Not changed: {len(not_changed)}\nUpdated: {len(updated)}\nCreated: {len(created)}\nRemoved: {len(removed)}")

    sync_dict = {}
    for slide in created:
        sync_dict[slide.get('id')] = 'creating'
    for slide in updated:
        sync_dict[slide.get('id')] = 'updating'
    sync_status[user_id] = sync_dict

    ApplicationPPTX = win32com.client.Dispatch("PowerPoint.Application")

    time.sleep(3)

    thread_pool.starmap(pres_sync_created, [(pres_conf_user_state, ApplicationPPTX, pres) for pres in created])

    thread_pool.starmap(pres_sync_updated, [(pres_conf_user_state, ApplicationPPTX, pres) for pres in updated])

    thread_pool.starmap(pres_sync_removed, [(pres_conf_user_state, pres) for pres in removed])

    ApplicationPPTX.Quit()
    ApplicationPPTX = None

    sync_status.pop(user_id)


@app.get('/presentations/sync-status')
def pres_sync_status(pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = user_session[pres_conf_user_state]
    if sync_status.get(user_id):
        return sync_status.get(user_id)
    else:
        return []


def pres_list_delta(new_pres_list, old_pres_list):
    not_changed = []
    updated = []
    created = []
    removed = []
    for new_pres in new_pres_list:
        found = False
        for old_pres in old_pres_list:
            if new_pres.get('id') == old_pres.get('id'):
                found = True
                if datetime.strptime(new_pres.get('modifiedTime'), '%Y-%m-%dT%H:%M:%S.%fZ') > old_pres.get(
                        'modified_time'):
                    updated.append(new_pres)
                    break
                not_changed.append(new_pres)
                break
        if not found:
            created.append(new_pres)

    for old_pres in old_pres_list:
        found = False
        for new_pres in new_pres_list:
            if new_pres.get('id') == old_pres.get('id'):
                found = True
                break
        if not found:
            removed.append(old_pres)
    return not_changed, updated, created, removed


def pres_sync_created(user_state, application, pres, loaded=False):
    user_id, user_flow = user_session[user_state]
    if not loaded: download_pres(user_state, pres)
    number_of_slides, slide_ratios = utils.extract_images(application, pres.get('id'))
    pres_text = utils.extract_text(pres.get('id'))

    db_handler.create(
        Presentations,
        id=pres.get('id'),
        name=pres.get('name'),
        owner_id=user_id,
        folder_id=pres.get('parents')[0],
        modified_time=pres.get('modifiedTime'),
    )

    for i in range(number_of_slides):
        with open(os.path.join(SROOT, f'presentations/temp/{pres.get("id")}/images/Слайд{i + 1}.png'), "rb") as image:
            img_bytes = image.read()

            db_handler.create(
                Slides,
                pres_id=pres.get('id'),
                index=i,
                thumbnail=img_bytes,
                text=pres_text[i],
                ratio=slide_ratios[i]
            )

    utils.clear_temp(pres)
    sync_status.get(user_id).pop(pres.get('id'))


def pres_sync_updated(user_state, application, pres):
    user_id, user_flow = user_session[user_state]
    if user_id == pres.get('owner_id'):
        db_handler.update(
            Presentations,
            obj_id=pres.get('id'),
            name=pres.get('name'),
            folder_id=pres.get('parents')[0],
            modified_time=pres.get('modifiedTime')
        )

        download_pres(user_state, pres)
        upd_slides_num = utils.extract_images(application, pres.get('id'))
        upd_thumbnails = utils.get_pres_thumbnails(pres, upd_slides_num)
        upd_pres_text = utils.extract_text(pres.get('id'))

        db_slides = db_handler.get_slides_index_asc(user_id, pres.get('id'))
        db_thumbnails = [slide.thumbnail for slide in db_slides]

        upd_eq_count = [0] * len(upd_thumbnails)

        for i, db_thumb in enumerate(db_thumbnails):
            pair = []
            for j, upd_thumb in enumerate(upd_thumbnails):
                if utils.img_eq(db_thumb, upd_thumb):
                    pair.append((j, upd_thumb))

            # Совпадений нет - слайд удален
            if len(pair) == 0:
                db_handler.delete(Slides, db_slides[i].id)

            # Одно совпадение - слайд остался в презентации
            # Если i == j - слайд остался на той же позиции
            # Иначе его переместили на позицию j
            elif len(pair) == 1:
                j, _ = pair[0]
                if i != j:
                    db_handler.update(
                        Slides,
                        obj_id=db_slides[i].id,
                        index=j
                    )
                upd_eq_count[j] += 1

            # Больше одного совпадения - в презентации несколько копий одного слайда
            # TODO
            else:
                pass

        for j, occurrences in enumerate(upd_eq_count):
            # Если при сравнении со старой презентацией (из БД)
            # не было ни одного совпадения со слайдом из новой презентации, то
            # этот слайд был добавлен
            if occurrences == 0:
                db_handler.create(
                    Slides,
                    pres_id=pres.get('id'),
                    index=j,
                    thumbnail=upd_thumbnails[j],
                    text=upd_pres_text[j]
                )

        utils.clear_temp(pres)


def pres_sync_removed(user_state, pres):
    user_id, user_flow = user_session[user_state]
    if user_id == pres.get('owner_id'):
        db_handler.delete(Presentations, pres.get('id'))


def pres_sync_uploaded(user_state, pres, pres_text, pres_thumbs, slides_from):
    user_id, user_flow = user_session[user_state]

    db_handler.create(
        Presentations,
        id=pres.get('id'),
        name=pres.get('name'),
        owner_id=user_id,
        folder_id=pres.get('parents')[0],
        modified_time=pres.get('modifiedTime'),
    )

    for i, (text, thumb) in enumerate(zip(pres_text, pres_thumbs)):
        _, slide = db_handler.create(
            Slides,
            pres_id=pres.get('id'),
            index=i,
            thumbnail=thumb,
            text=text
        )
        migrate_tags(slides_from[i], slide)


@app.get('/slides/by-pres-id')
def get_pres_slides(pres_id, pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = user_session[pres_conf_user_state]
    pres_slides = db_handler.get_slides_index_asc(user_id, pres_id)
    return [slide.json() for slide in pres_slides]


@app.get('/slides/by-text')
def get_slides_by_text(search_phrase, pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = user_session[pres_conf_user_state]
    slides_found = [slide for slide in db_handler.get_slides_by_text(user_id, search_phrase)]
    result = []
    for slide in slides_found:
        pres = db_handler.read(Presentations, slide.pres_id)
        result.append({**Slides(**slide).json(), 'pres_name': pres.name})
    return result


@app.get('/slides/by-tag-query')
def get_slides_by_query(query, pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = user_session[pres_conf_user_state]

    tag_names = re.findall('[a-z]+[a-z0-9]*', query)
    tag_names = [tag for tag in tag_names if tag not in ['and', 'or', 'not']]

    links_and_tags = db_handler.get_links_and_tags(user_id, tag_names)

    slides_tags_values = {}
    for link, tag in links_and_tags:
        if slides_tags_values.get(link.slide_id) is None:
            slides_tags_values[link.slide_id] = {key: False for key in tag_names}

        if link.value is not None:
            slides_tags_values[link.slide_id][tag.name] = link.value
        else:
            slides_tags_values[link.slide_id][tag.name] = True

    filtered_slides = []

    for slide_id in slides_tags_values.keys():
        eval_query = query
        for tag in slides_tags_values[slide_id].keys():
            eval_query = eval_query.replace(tag, str(slides_tags_values[slide_id][tag]))
        if eval(eval_query):
            filtered_slides.append(slide_id)

    found_slides = db_handler.findall(Slides, Slides.id.in_(filtered_slides))

    result = []
    for slide in found_slides:
        id = slide.pres_id
        pres = db_handler.read(Presentations, id)
        result.append({**slide.json(), 'pres_name': pres.name})

    sorted_result = sorted(result, key=lambda slide: slide.get('pres_name'))

    return sorted_result


@app.post('/presentations/build')
def build_pres(new_pres: BuildPresentationModel, pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = user_session[pres_conf_user_state]

    if len(new_pres.build_from) == 0: return None

    pres_to_download = []
    for slide in new_pres.build_from:
        if slide.pres_id not in pres_to_download:
            pres_to_download.append(slide.pres_id)

    thread_pool.starmap(
        download_pres,
        [(pres_conf_user_state, {'id': pres_id}) for pres_id in pres_to_download]
    )

    with slides.Presentation() as presentation:
        presentation.slide_size.set_size(
            slides.SlideSizeType.ON_SCREEN_16X9,
            slides.SlideSizeScaleType.DO_NOT_SCALE
        )
        presentation.slides.remove_at(0)

        seen_thumbs = []
        seen_text = []
        seen_slides = []

        for slide in new_pres.build_from:
            with slides.Presentation(
                    os.path.join(SROOT, f"presentations/temp/{slide.pres_id}/{slide.pres_id}.pptx")
            ) as pres_from:
                pres_text = utils.extract_text(slide.pres_id)
                unique = True
                slide_thumb = db_handler.get_slide_thumb_by_index(user_id, slide.pres_id, slide.index)
                slide_text = pres_text[slide.index]
                for seen_thumb in seen_thumbs:
                    if utils.img_eq(slide_thumb, seen_thumb):
                        unique = False
                        break
                if unique:
                    presentation.slides.add_clone(pres_from.slides[slide.index])

                    seen_thumbs.append(slide_thumb)
                    seen_text.append(slide_text)
                    seen_slides.append(slide)

        for pres_id in pres_to_download:
            utils.clear_temp({'id': pres_id})

        presentation.save(
            os.path.join(SROOT, f'presentations/generated/{new_pres.name}.pptx'),
            slides.export.SaveFormat.PPTX
        )
        utils.clear_watermark(os.path.join(SROOT, f'presentations/generated/{new_pres.name}.pptx'))

    pres = upload_pres(pres_conf_user_state, new_pres.name)
    pres_sync_uploaded(pres_conf_user_state, pres, seen_text, seen_thumbs, seen_slides)
    return pres


@app.get('/presentations/download')
def download_built_pres(pres_id, pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = user_session[pres_conf_user_state]
    pres = db_handler.read(Presentations, pres_id)
    if pres.owner_id == user_id:
        return FileResponse(
            os.path.join(SROOT, f'presentations/generated/{pres.name}'))


@app.post('/links/create')
def create_link(slide_id, tag_name, value=None, pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = user_session[pres_conf_user_state]

    slide = db_handler.read(Slides, slide_id)
    if slide is None:
        return 'Slide does not exist'

    tag_created, tag = db_handler.find_or_create(
        Tags,
        Tags.owner_id == user_id, Tags.name == tag_name,
        name=tag_name,
        owner_id=user_id
    )
    link_created, link = db_handler.find_or_create(
        Links,
        Links.slide_id == slide_id, Links.tag_id == tag.id,
        slide_id=slide_id,
        tag_id=tag.id,
        value=value
    )
    if not link_created:
        db_handler.update(Links, link.id, value=value)
        return 'Link updated'

    return 'Link created'


@app.post('/links/remove')
def remove_link(slide_id, tag_name, pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = user_session[pres_conf_user_state]

    tag = db_handler.find(Tags, Tags.owner_id == user_id, Tags.name == tag_name)
    if tag is None:
        return "Tag does not exists"
    link = db_handler.find(Links, Links.slide_id == slide_id, Links.tag_id == tag.id)
    if link is None:
        return "Link does not exists"
    db_handler.delete(Links, link.id)


@app.get('/links/slide-tags')
def get_slide_tags(slide_id):
    links = db_handler.findall(Links, Links.slide_id == slide_id)
    tags = []
    for link in links:
        tag = db_handler.find(Tags, Tags.id == link.tag_id)
        tags.append({'id': tag.id, 'name': tag.name, 'owner_id': tag.owner_id, 'value': link.value})
    return tags


def download_pres(user_state, pres):
    try:
        user_id, user_flow = user_session[user_state]
        credentials = user_flow.credentials
        drive = build('drive', 'v3', credentials=credentials)
        request = drive.files().get_media(fileId=pres.get('id'))
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    pres_dir_path = os.path.join(SROOT, f"presentations/temp/{pres.get('id')}")
    os.mkdir(pres_dir_path)
    with open(f"{pres_dir_path}/{pres.get('id')}.pptx", "wb") as f:
        f.write(file.getvalue())


def upload_pres(user_state, pres_name):
    user_id, user_flow = user_session[user_state]
    credentials = user_flow.credentials
    drive = build('drive', 'v3', credentials=credentials)
    file_metadata = {
        'name': f'{pres_name}.pptx'
    }
    media = MediaFileUpload(
        os.path.join(SROOT, f"presentations/generated/{pres_name}.pptx"),
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )
    file = drive.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, modifiedTime, parents').execute()
    return file


def migrate_tags(slide_from, slide_to):
    slide_from_links = db_handler.findall(Links, Links.slide_id == slide_from.id)
    for link in slide_from_links:
        db_handler.find_or_create(
            Links,
            Links.slide_id == slide_to.id, Links.tag_id == link.tag_id,
            slide_id=slide_to.id,
            tag_id=link.tag_id,
            value=link.value
        )


if __name__ == "__main__":
    if origin == "https://pres-configurator.ru":
        uvicorn.run("main:app", host="0.0.0.0", port=443, log_level="info",
                    ssl_keyfile='ssl/private.key',
                ssl_certfile='ssl/certificate.crt')
    elif origin == "http://localhost:8000":
        uvicorn.run("main:app", host="localhost", port=8000, log_level="info")
