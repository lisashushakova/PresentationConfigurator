import io
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

from app.definitions import SERVER_ROOT


class GoogleDriveHandler:

    def __init__(self, pool):
        self.pool = pool

    def get_user_file_tree(self, user_flow):
        drive_service = build('drive', 'v3', credentials=user_flow.credentials)

        drive = drive_service.files().get(fileId='root', fields='id, name').execute()
        folders = [drive]

        presentations = drive_service.files().list(
            q=f"mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation' " \
              "and trashed = false",
            fields='files(id, name, modifiedTime, parents)').execute().get('files')

        def traverse(node):
            children = drive_service.files().list(
                q=f"mimeType='application/vnd.google-apps.folder' and not trashed and '{node.get('id')}' in parents",
                fields='files(id, name)').execute().get('files')
            for child in children:
                traverse(child)
                folders.append(child)
            for pres in presentations:
                if pres.get('parents')[0] == node.get('id'):
                    children.append(pres)
                    pres['type'] = 'presentation'
            node['children'] = children
            node['type'] = 'folder'

        traverse(drive)
        file_tree = drive
        return folders, presentations, file_tree

    def __download_presentation(self, presentation, user_flow):

        try:
            drive_service = build('drive', 'v3', credentials=user_flow.credentials)
            request = drive_service.files().get_media(fileId=presentation.get('id'))
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

            if not os.path.exists(os.path.join(SERVER_ROOT, f"presentation_processing/temp")):
                os.mkdir(os.path.join(SERVER_ROOT, f"presentation_processing/temp"))

            pres_dir_path = os.path.join(SERVER_ROOT, f"presentation_processing/temp/{presentation.get('id')}")
            if not os.path.exists(pres_dir_path):
                os.mkdir(pres_dir_path)

            with open(f"presentation_processing/temp/{presentation.get('id')}/{presentation.get('id')}.pptx",
                      "wb") as f:
                f.write(file.getvalue())

        except HttpError as error:
            print(F'An error occurred: {error}')

    def download_presentations(self, presentations, user_flow):
        temp_path = os.path.join(SERVER_ROOT, "presentation_processing/temp")
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)
        self.pool.starmap(self.__download_presentation, [(pres, user_flow) for pres in presentations])

    def upload_presentation(self, name, save_to, user_id, user_flow):
        credentials = user_flow.credentials
        drive = build('drive', 'v3', credentials=credentials)
        file_metadata = {
            'name': f'{name}.pptx',
        }
        if save_to is not None:
            file_metadata['parents'] = [save_to]
        media = MediaFileUpload(
            os.path.join(SERVER_ROOT, f"presentation_processing/built/{user_id}/{name}.pptx"),
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        file = drive.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, modifiedTime, parents').execute()
        return file
