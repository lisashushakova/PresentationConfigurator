import os
import re
from multiprocessing.pool import ThreadPool

import fastapi
import uvicorn as uvicorn
from fastapi import Cookie
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response, FileResponse

from app.definitions import ROOT, SERVER_ROOT, db_user, db_password, db_url, db_name, api_origin, frontend_origin
from app.server.main.database.database_handler import DatabaseHandler, Users
from app.server.main.external_services.google.google_auth_handler import GoogleAuthHandler
from app.server.main.external_services.google.google_drive_handler import GoogleDriveHandler
from app.server.main.interfaces.build_presentation_model import BuildPresentationModel
from app.server.main.interfaces.filter_model import FilterModel
from app.server.main.interfaces.filtered_slides_model import FilteredSlidesModel
from app.server.main.interfaces.slides_pool_model import SlidesPoolModel
from app.server.main.interfaces.style_templates_model import StyleTemplatesModel
from app.server.main.interfaces.user_tags_list_model import UserTagsListModel
from app.server.main.interfaces.file_tree_model import FolderModel
from app.server.main.interfaces.presentation_slides_model import PresentationSlidesModel
from app.server.main.interfaces.presentations_list_model import PresentationsListModel
from app.server.main.interfaces.tags_list_model import TagListModel
from app.server.main.interfaces.user_info_model import UserInfoModel
from app.server.main.presentation_processing.presentation_process_handler import PresentationProcessHandler
from dotenv import load_dotenv
from utils import utils

load_dotenv()

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[api_origin, frontend_origin, 'http://localhost'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_sessions = {}
pool = ThreadPool(processes=20)

db_handler = DatabaseHandler(
    pool=pool,
    user=db_user,
    password=db_password,
    host=db_url,
    db=db_name
)

db_handler.create_db()

auth_handler = GoogleAuthHandler(pool=pool)
drive_handler = GoogleDriveHandler(pool=pool)
pres_handler = PresentationProcessHandler(pool=pool)


# ---------- AUTH BLOCK ----------

@app.get('/auth/login')
def auth():
    redirect = auth_handler.get_auth_redirect()
    return redirect


@app.get('/auth/sessions')
def sessions(code, state):
    user_id, user_name = auth_handler.set_session(code, state)
    db_handler.find_or_create(Users, Users.id == user_id, id=user_id, name=user_name)
    redirect = auth_handler.get_auth_done_redirect(state)
    return redirect


@app.get('/auth/user-info', response_model=UserInfoModel)
def user_info(pres_conf_user_state: str = Cookie(default=None)):
    username, icon_url = auth_handler.get_user_info(pres_conf_user_state)
    res = {
        'username': username,
        'iconURL': icon_url
    }
    return res


@app.post('/auth/logout')
def logout(pres_conf_user_state: str = Cookie(default=None)):
    logout_response = auth_handler.logout(pres_conf_user_state)
    return logout_response


# ---------- FILES BLOCK ----------


@app.get('/files/tree', response_model=FolderModel)
def file_tree(pres_conf_user_state: str = Cookie(default=None), only_folders=False):
    user_id, user_flow = auth_handler.get_user(pres_conf_user_state)
    drive_folders, drive_presentations, user_file_tree = drive_handler.get_user_file_tree(user_flow)
    user_file_tree['is_root'] = True
    marked_presentations = []

    db_folders = db_handler.sync_folders(user_id, drive_folders)

    def traverse(node):
        for db_folder in db_folders:
            if node.get('id') == db_folder.id:
                if node.get('is_root'):
                    node['mark'] = True
                else:
                    node['mark'] = db_folder.mark
                break

        for child in node.get('children'):
            if child.get('type') == 'folder':
                traverse(child)
            elif child.get('type') == 'presentation' and node.get('mark'):
                marked_presentations.append(child)

    traverse(user_file_tree)

    if not only_folders:
        try:
            presentations_to_sync, delta = db_handler.sync_presentations(user_id, marked_presentations)
            drive_handler.download_presentations(presentations_to_sync, user_flow)
            presentations_ratio = pres_handler.crop_presentations(presentations_to_sync)
            presentations_text = pres_handler.extract_text(presentations_to_sync)
            db_handler.sync_presentation_slides(presentations_to_sync, delta, presentations_ratio, presentations_text, user_id)
        finally:
            utils.clear_temp()

    return user_file_tree


@app.get('/files/sync-status')
def get_sync_status(pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    return db_handler.get_sync_query(user_id)


@app.post('/files/folders/set-mark')
def set_folder_preference(folder_id, value, pres_conf_user_state: str = Cookie(default=None)):
    # Convert js' boolean to python boolean
    value = value == 'true'

    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    db_handler.set_folder_mark(user_id, folder_id, value)


# ---------- SLIDES BLOCK ----------

@app.get('/slides/by-pres-id', response_model=PresentationSlidesModel)
def get_pres_slides(pres_id, pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    pres_slides = db_handler.get_slides_index_asc(pres_id)
    return {'slides': [slide.json() for slide in pres_slides]}


@app.post('/slides/by-filters', response_model=FilteredSlidesModel)
def get_slides_by_filters(filters: FilterModel, pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    slides_with_labels = db_handler.get_slides_by_filters(
        filters.presentations,
        filters.tag_query,
        filters.text_phrase,
        filters.ratio,
        user_id
    )
    return {'slides': slides_with_labels}


# ---------- PRESENTATIONS BLOCK ----------
@app.get('/presentations/by-tag-query', response_model=PresentationsListModel)
def get_presentations_by_tag_query(query, pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    presentations = db_handler.get_presentations_by_tag_query(query, user_id)
    return {'filtered_presentations': presentations}


@app.post('/presentations/generate-style-templates', response_model=StyleTemplatesModel)
def generate_style_templates(slides: SlidesPoolModel, pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = auth_handler.get_user(pres_conf_user_state)
    presentations = [{'id': pres_id} for pres_id in set([slide.pres_id for slide in slides.slides])]
    try:
        drive_handler.download_presentations(presentations, user_flow)
        templates = pres_handler.create_style_templates(presentations)
        return {'templates': templates}
    finally:
        utils.clear_temp()
        utils.clear_styles()


@app.post('/presentations/build')
def build_presentations(build_from: BuildPresentationModel, pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = auth_handler.get_user(pres_conf_user_state)
    presentations = [{'id': pres_id} for pres_id in set([slide.pres_id for slide in build_from.slides])]
    try:
        drive_handler.download_presentations(presentations, user_flow)
        seen_text, seen_thumbs, seen_slides = pres_handler.build_presentation(
            build_from.name, build_from.slides, build_from.ratio, build_from.style_template, db_handler, user_id)
        pres = drive_handler.upload_presentation(build_from.name, build_from.save_to, user_id, user_flow)
        db_handler.pres_sync_uploaded(pres, seen_text, seen_thumbs, build_from.ratio, seen_slides, user_id)
    finally:
        utils.clear_temp()


@app.get('/presentations/get-built-presentation')
def get_built_presentation(pres_name, pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = auth_handler.get_user(pres_conf_user_state)
    return FileResponse(os.path.join(SERVER_ROOT, f'presentation_processing/built/{user_id}/{pres_name}.pptx'))


@app.post('/presentations/clear-built')
def clear_built_presentations(pres_conf_user_state: str = Cookie(default=None)):
    user_id, user_flow = auth_handler.get_user(pres_conf_user_state)
    utils.clear_user_built(user_id)


# ---------- TAGS BLOCK ----------
@app.get('/tags/tags-list', response_model=UserTagsListModel)
def get_user_tags_list(pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    presentation_tags, slide_tags = db_handler.get_user_tags_list(user_id)
    return {'presentations_tags': presentation_tags, 'slides_tags': slide_tags}


# ---------- LINKS BLOCK ----------

@app.get('/links/slide-links', response_model=TagListModel)
def get_slide_links(slide_id, pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    slide_links = db_handler.get_slide_links(int(slide_id), user_id)
    return {'links': slide_links}


@app.post('/links/create-slide-link')
def create_slide_link(slide_id, tag_name, value, pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    if value == '':
        value = None
    db_handler.create_slide_link(int(slide_id), tag_name, value, user_id)


@app.post('/links/remove-slide-link')
def remove_slide_link(slide_id, tag_name, pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    db_handler.remove_slide_link(int(slide_id), tag_name, user_id)


@app.get('/links/presentation-links', response_model=TagListModel)
def get_slide_links(presentation_id, pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    slide_links = db_handler.get_presentation_links(presentation_id, user_id)
    return {'links': slide_links}


@app.post('/links/create-presentation-link')
def create_slide_link(presentation_id, tag_name, value, pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    if value == '':
        value = None
    db_handler.create_presentation_link(presentation_id, tag_name, value, user_id)


@app.post('/links/remove-presentation-link')
def remove_slide_link(presentation_id, tag_name, pres_conf_user_state: str = Cookie(default=None)):
    user_id, _ = auth_handler.get_user(pres_conf_user_state)
    db_handler.remove_presentation_link(presentation_id, tag_name, user_id)



if __name__ == "__main__":
    m = re.match(r'http://(?P<host>.*):(?P<port>.*)', api_origin)
    uvicorn.run("main:app", host=m.group('host'), port=int(m.group('port')), log_level="info")
