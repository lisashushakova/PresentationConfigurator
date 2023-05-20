import datetime
import os
import shutil
import unittest
from multiprocessing.pool import ThreadPool

import pythoncom
import win32com.client
from aspose import slides

from app.definitions import SERVER_ROOT, db_user, db_password, db_url, db_name
from app.server.main.database.database_handler import Slides, DatabaseHandler, Users, Presentations
from app.server.main.presentation_processing.presentation_process_handler import PresentationProcessHandler
from app.server.main.utils.utils import clear_temp, clear_styles, clear_user_built


class PresentationProcessingTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pool = ThreadPool(processes=20)
        cls.pres_handler = PresentationProcessHandler(pool)

        cls.db_handler = DatabaseHandler(
            pool=pool,
            user=db_user,
            password=db_password,
            host=db_url,
            db=db_name,
            echo=False
        )
        cls.db_handler.clear_db()

    def test_crop_presentations(self):
        try:
            temp_path = os.path.join(SERVER_ROOT, 'presentation_processing/temp')
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)

            presentation1 = {
                'id': 'pres1id',
                'name': 'TEST_PRESENTATION_1_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres1_path = os.path.join(temp_path, f'{presentation1.get("id")}')
            if not os.path.exists(pres1_path):
                os.mkdir(pres1_path)
            shutil.copyfile('files/pres1id.pptx', os.path.join(pres1_path, 'pres1id.pptx'))

            presentation2 = {
                'id': 'pres2id',
                'name': 'TEST_PRESENTATION_2_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres2_path = os.path.join(temp_path, f'{presentation2.get("id")}')
            if not os.path.exists(pres2_path):
                os.mkdir(pres2_path)
            shutil.copyfile('files/pres2id.pptx', os.path.join(pres2_path, 'pres2id.pptx'))

            presentation3 = {
                'id': 'pres3id',
                'name': 'TEST_PRESENTATION_3_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres3_path = os.path.join(temp_path, f'{presentation3.get("id")}')
            if not os.path.exists(pres3_path):
                os.mkdir(pres3_path)
            shutil.copyfile('files/pres3id.pptx', os.path.join(pres3_path, 'pres3id.pptx'))

            pythoncom.CoInitializeEx(0)
            ApplicationPPTX = win32com.client.Dispatch("PowerPoint.Application")

            ratio1 = self.pres_handler.crop_presentation(presentation1, ApplicationPPTX)
            ratio2 = self.pres_handler.crop_presentation(presentation2, ApplicationPPTX)
            ratio3 = self.pres_handler.crop_presentation(presentation3, ApplicationPPTX)

            assert len(os.listdir(os.path.join(pres1_path, 'images'))) == 2
            assert ratio1 == Slides.Ratio.WIDESCREEN_16_TO_9
            assert len(os.listdir(os.path.join(pres2_path, 'images'))) == 2
            assert ratio2 == Slides.Ratio.WIDESCREEN_16_TO_9
            assert len(os.listdir(os.path.join(pres3_path, 'images'))) == 2
            assert ratio3 == Slides.Ratio.STANDARD_4_TO_3

            ApplicationPPTX.Quit()
            ApplicationPPTX = None
        finally:
            clear_temp()

    def test_extract_text(self):
        try:
            temp_path = os.path.join(SERVER_ROOT, 'presentation_processing/temp')
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)

            presentation1 = {
                'id': 'pres1id',
                'name': 'TEST_PRESENTATION_1_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres1_path = os.path.join(temp_path, f'{presentation1.get("id")}')
            if not os.path.exists(pres1_path):
                os.mkdir(pres1_path)
            shutil.copyfile('files/pres1id.pptx', os.path.join(pres1_path, 'pres1id.pptx'))

            presentation2 = {
                'id': 'pres2id',
                'name': 'TEST_PRESENTATION_2_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres2_path = os.path.join(temp_path, f'{presentation2.get("id")}')
            if not os.path.exists(pres2_path):
                os.mkdir(pres2_path)
            shutil.copyfile('files/pres2id.pptx', os.path.join(pres2_path, 'pres2id.pptx'))

            presentation3 = {
                'id': 'pres3id',
                'name': 'TEST_PRESENTATION_3_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres3_path = os.path.join(temp_path, f'{presentation3.get("id")}')
            if not os.path.exists(pres3_path):
                os.mkdir(pres3_path)
            shutil.copyfile('files/pres3id.pptx', os.path.join(pres3_path, 'pres3id.pptx'))

            presentations_text = self.pres_handler.extract_text([presentation1, presentation2, presentation3])
            assert 'Презентация 1' in presentations_text[0]
            assert 'Слайд 1Текст презентации 1' in presentations_text[0]

            assert 'Презентация 2' in presentations_text[1]
            assert 'Слайд 2Текст презентации 2' in presentations_text[1]

            assert 'Презентация 3' in presentations_text[2]
            assert 'Слайд 3Текст презентации 3' in presentations_text[2]
        finally:
            clear_temp()

    def test_create_style_templates(self):
        try:
            temp_path = os.path.join(SERVER_ROOT, 'presentation_processing/temp')
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)

            presentation1 = {
                'id': 'pres1id',
                'name': 'TEST_PRESENTATION_1_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres1_path = os.path.join(temp_path, f'{presentation1.get("id")}')
            if not os.path.exists(pres1_path):
                os.mkdir(pres1_path)
            shutil.copyfile('files/pres1id.pptx', os.path.join(pres1_path, 'pres1id.pptx'))

            presentation2 = {
                'id': 'pres2id',
                'name': 'TEST_PRESENTATION_2_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres2_path = os.path.join(temp_path, f'{presentation2.get("id")}')
            if not os.path.exists(pres2_path):
                os.mkdir(pres2_path)
            shutil.copyfile('files/pres2id.pptx', os.path.join(pres2_path, 'pres2id.pptx'))

            presentation3 = {
                'id': 'pres3id',
                'name': 'TEST_PRESENTATION_3_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres3_path = os.path.join(temp_path, f'{presentation3.get("id")}')
            if not os.path.exists(pres3_path):
                os.mkdir(pres3_path)
            shutil.copyfile('files/pres3id.pptx', os.path.join(pres3_path, 'pres3id.pptx'))

            style_path = os.path.join(SERVER_ROOT, "presentation_processing/styles/temp")
            if not os.path.exists(style_path):
                os.mkdir(style_path)

            pythoncom.CoInitializeEx(0)
            ApplicationPPTX = win32com.client.Dispatch("PowerPoint.Application")

            style_template_1 = self.pres_handler.create_style_template(presentation1, ApplicationPPTX)
            assert style_template_1 is not None
            assert style_template_1.get('id') == presentation1.get('id')

            style_template_2 = self.pres_handler.create_style_template(presentation2, ApplicationPPTX)
            assert style_template_2 is not None
            assert style_template_2.get('id') == presentation2.get('id')

            style_template_3 = self.pres_handler.create_style_template(presentation3, ApplicationPPTX)
            assert style_template_3 is not None
            assert style_template_3.get('id') == presentation3.get('id')

            ApplicationPPTX.Quit()
            ApplicationPPTX = None

        finally:
            clear_temp()
            clear_styles()

    def test_build_presentation(self):
        user = self.create_test_user()
        try:

            temp_path = os.path.join(SERVER_ROOT, 'presentation_processing/temp')
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)

            presentation1 = {
                'id': 'pres1id',
                'name': 'TEST_PRESENTATION_1_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres1_path = os.path.join(temp_path, f'{presentation1.get("id")}')
            if not os.path.exists(pres1_path):
                os.mkdir(pres1_path)
            shutil.copyfile('files/pres1id.pptx', os.path.join(pres1_path, 'pres1id.pptx'))

            presentation2 = {
                'id': 'pres2id',
                'name': 'TEST_PRESENTATION_2_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            pres2_path = os.path.join(temp_path, f'{presentation2.get("id")}')
            if not os.path.exists(pres2_path):
                os.mkdir(pres2_path)
            shutil.copyfile('files/pres2id.pptx', os.path.join(pres2_path, 'pres2id.pptx'))

            self.db_handler.sync_presentations(user.id, [presentation1, presentation2])

            with open('files/slide_thumbnail_1.png', 'rb') as file:
                self.create_slide_sample(pres_id=presentation1.get('id'), index=0, thumbnail=file.read())

            with open('files/slide_thumbnail_2.png', 'rb') as file:
                self.create_slide_sample(pres_id=presentation1.get('id'), index=1, thumbnail=file.read())

            with open('files/slide_thumbnail_3.png', 'rb') as file:
                self.create_slide_sample(pres_id=presentation2.get('id'), index=0, thumbnail=file.read())

            with open('files/slide_thumbnail_4.png', 'rb') as file:
                self.create_slide_sample(pres_id=presentation2.get('id'), index=1, thumbnail=file.read())

            pres1_slides = self.db_handler.get_slides_index_asc(presentation1.get('id'))
            pres2_slides = self.db_handler.get_slides_index_asc(presentation2.get('id'))

            name = 'NEW_PRESENTATION'
            slides_from = [*pres1_slides, *pres2_slides]
            ratio = Slides.Ratio.STANDARD_4_TO_3
            style_template = None

            self.pres_handler.build_presentation(name, slides_from, ratio, style_template, self.db_handler, user.id)

            pres_path = os.path.join(SERVER_ROOT, f"presentation_processing/built/{user.id}/{name}.pptx")
            assert os.path.exists(pres_path)

            with slides.Presentation(pres_path) as new_pres:
                assert len(new_pres.slides) == 4

        finally:
            clear_temp()
            clear_user_built(user.id)


    # ---------------------------Utilities-------------------------------

    def create_test_user(self):
        created, user = self.db_handler.create(Users, **{
            'id': 'TEST_USER_ID',
            'name': 'TEST_USER',
        })

        assert created

        return user

    def create_pres_sample(self, id='TEST_PRESENTATION_ID', owner_id='TEST_USER_ID', name='TEST_PRESENTATION', dt=None):
        if dt is None:
            dt = datetime.datetime.fromisoformat('2023-05-01')

        created, presentation = self.db_handler.create(Presentations, **{
            'id': id,
            'name': name,
            'owner_id': owner_id,
            'modified_time': dt
        })

        assert created

        return presentation

    def create_slide_sample(self, pres_id='TEST_PRESENTATION_ID', index=0, thumbnail=None, text='SLIDE_TEXT',
                            ratio=Slides.Ratio.STANDARD_4_TO_3):
        with open('files/slide_thumbnail_1.png', "rb") as file:
            created, slide = self.db_handler.create(Slides, **{
                'pres_id': pres_id,
                'index': index,
                'thumbnail': file.read() if thumbnail is None else thumbnail,
                'text': text,
                'ratio': ratio
            })

            assert created

        return slide



    @classmethod
    def tearDownClass(cls) -> None:
        cls.db_handler.clear_db()
        cls.pres_handler.pool.close()

if __name__ == '__main__':
    unittest.main()