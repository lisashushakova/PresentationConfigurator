import os

import dotenv

dotenv.load_dotenv()

ROOT = os.path.dirname(os.path.abspath(__file__))
SERVER_ROOT = os.path.join(ROOT, 'server/main')

api_origin = os.environ['PRESENTATION_CONFIGURATOR_API_ORIGIN']
frontend_origin = os.environ['PRESENTATION_CONFIGURATOR_FRONTEND_ORIGIN']

db_user = os.environ['PRESENTATION_CONFIGURATOR_DATABASE_USER']
db_password = os.environ['PRESENTATION_CONFIGURATOR_DATABASE_PASSWORD']
db_url = os.environ['PRESENTATION_CONFIGURATOR_DATABASE_URL']
db_name = os.environ['PRESENTATION_CONFIGURATOR_DATABASE_NAME']

