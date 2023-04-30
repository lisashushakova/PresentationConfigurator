import hashlib
import os

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from starlette.responses import RedirectResponse, Response

from app.definitions import api_origin


class GoogleAuthHandler:

    def __init__(self, pool):
        self.user_sessions = {}
        self.pool = pool

    def get_auth_redirect(self):
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        default_auth_flow = Flow.from_client_secrets_file(
            'external_services/google/oauth2.keys.json',
            scopes=['openid',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'https://www.googleapis.com/auth/drive.readonly',
                    'https://www.googleapis.com/auth/drive.file'
                    ],
            redirect_uri=api_origin + '/auth/sessions'
        )
        self.user_sessions[state] = [None, default_auth_flow]
        auth_url, _ = default_auth_flow.authorization_url(
            access_type='offline',
            state=state
        )
        return RedirectResponse(url=auth_url)

    def set_session(self, code, state):
        _, user_flow = self.user_sessions[state]
        user_flow.fetch_token(code=code)
        user_info_service = build('oauth2', 'v2', credentials=user_flow.credentials)
        user_info = user_info_service.userinfo().get().execute()

        user_id = user_info['id']
        user_name = user_info['name']

        self.user_sessions[state] = [user_id, user_flow]

        return user_id, user_name

    def get_auth_done_redirect(self, state):
        response = RedirectResponse(url="http://localhost:3000/")
        response.set_cookie(key="pres_conf_user_state", value=state)
        return response

    def get_user_info(self, state):
        _, user_flow = self.user_sessions[state]

        user_info_service = build('oauth2', 'v2', credentials=user_flow.credentials)
        user_info = user_info_service.userinfo().get().execute()

        user_name = user_info['name']
        picture_url = user_info['picture']

        return user_name, picture_url

    def logout(self, state):
        try:
            self.user_sessions.pop(state)
        finally:
            response = Response()
            response.delete_cookie(key="pres_conf_user_state")
            return response

    def get_user(self, state):
        return self.user_sessions[state]