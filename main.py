import fastapi
import uvicorn as uvicorn
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from starlette.responses import RedirectResponse
from database.db_handler import DatabaseHandler

app = fastapi.FastAPI()


db_handler = DatabaseHandler()
flow = Flow.from_client_secrets_file(
        'auth/oauth2.keys.json',
        scopes=['openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/drive'],
        redirect_uri="http://localhost:8000/auth/sessions"
    )


@app.get('/auth/login')
def login():
    auth_uri = flow.authorization_url()[0]
    return RedirectResponse(url=auth_uri)


@app.get('/auth/sessions')
def sessions(code):
    flow.fetch_token(code=code)
    credentials = flow.credentials
    user_info_service = build('oauth2', 'v2', credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()
    if db_handler.users.


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")