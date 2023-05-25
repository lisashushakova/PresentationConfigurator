import base64
import datetime
import ntpath
import os
import shutil
import typing
import unittest

from app.server.main.utils.utils import clear_temp

unittest.TestLoader.sortTestMethodsUsing = None

from multiprocessing.pool import ThreadPool


from app.definitions import db_user, db_password, db_url, db_name, SERVER_ROOT
from app.server.main.database.database_handler import DatabaseHandler, Users, Presentations, Slides, Tags, SlideLinks, \
    Folders, PresentationLinks


class DatabaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pool = ThreadPool(processes=20)
        cls.db_handler = DatabaseHandler(
            pool=pool,
            user=db_user,
            password=db_password,
            host=db_url,
            db=db_name,
            echo=False
        )
        cls.db_handler.clear_db()

    def setUp(self):
        self.db_handler.clear_db()

    def test_user_create(self):
        created, user = self.db_handler.create(Users, **{
            'id': 'TEST_USER_ID',
            'name': 'TEST_USER',
        })
        users = self.db_handler.findall(Users)
        usernames = [user.name for user in users]
        assert created and 'TEST_USER' in usernames

        created, user = self.db_handler.create(Users, **{
            'id': 'TEST_USER_ID',
            'name': 'TEST_USER',
        })

        assert not created

    def test_user_update(self):
        created, user = self.db_handler.create(Users, **{
            'id': 'TEST_USER_ID',
            'name': 'TEST_USER',
        })
        self.db_handler.update(Users, 'TEST_USER_ID', **{
            'name': 'UPDATED_TEST_USER_NAME'
        })
        user = self.db_handler.read(Users, 'TEST_USER_ID')
        assert user.name == 'UPDATED_TEST_USER_NAME'

    def test_user_delete(self):
        created, user = self.db_handler.create(Users, **{
            'id': 'TEST_USER_ID',
            'name': 'TEST_USER',
        })
        self.db_handler.delete(Users, 'TEST_USER_ID')
        users = self.db_handler.findall(Users)
        usernames = [user.name for user in users]
        assert 'TEST_USER' not in usernames

    def test_find_or_create(self):
        created, user = self.db_handler.find_or_create(
            Users,
            Users.name == 'TEST_USER',
            **{
                'id': 'TEST_USER_ID',
                'name': 'TEST_USER',
            }
        )

        users = self.db_handler.findall(Users)
        usernames = [user.name for user in users]
        assert created and 'TEST_USER' in usernames

        created, user = self.db_handler.find_or_create(
            Users,
            Users.name == 'TEST_USER',
            **{
                'id': 'TEST_USER_ID',
                'name': 'TEST_USER',
            }
        )

        assert not created

    def test_get_presentations_as_json(self):
        self.create_test_user()

        dt = datetime.datetime.fromisoformat('2023-05-01')
        created, presentation = self.db_handler.create(Presentations, **{
            'id': 'TEST_PRESENTATION_ID',
            'name': 'TEST_PRESENTATION',
            'owner_id': 'TEST_USER_ID',
            'modified_time': dt
        })

        assert created

        pres_json = presentation.json()

        assert type(pres_json) is dict

        assert pres_json['id'] and pres_json['id'] == 'TEST_PRESENTATION_ID'
        assert pres_json['name'] and pres_json['name'] == 'TEST_PRESENTATION'
        assert pres_json['owner_id'] and pres_json['owner_id'] == 'TEST_USER_ID'
        assert pres_json['modified_time'] and pres_json['modified_time'] == str(dt)


    def test_get_slides_as_json(self):
        self.create_test_user()

        self.create_pres_sample()
        slide = self.create_slide_sample()

        slide_json = slide.json()

        assert type(slide_json) is dict

        assert 'pres_id' in slide_json and slide_json['pres_id'] == 'TEST_PRESENTATION_ID'
        assert 'index' in slide_json and slide_json['index'] == 0
        assert 'text' in slide_json and slide_json['text'] == 'SLIDE_TEXT'
        assert 'thumbnail' in slide_json
        assert 'ratio' in slide_json and slide_json['ratio'] == Slides.Ratio.STANDARD_4_TO_3.value

    def test_get_slides_index_asc(self):
        self.create_test_user()

        slides_index_asc = self.db_handler.get_slides_index_asc('TEST_PRESENTATION_ID')
        assert slides_index_asc is None

        self.create_pres_sample()
        self.create_slide_sample(index=0)
        self.create_slide_sample(index=2)
        self.create_slide_sample(index=1)

        slides_index_asc = self.db_handler.get_slides_index_asc('TEST_PRESENTATION_ID')

        assert len(slides_index_asc) == 3
        assert slides_index_asc[0].index < slides_index_asc[1].index < slides_index_asc[2].index

    def test_get_links_and_tags(self):
        self.create_test_user()

        self.create_pres_sample()

        slide1 = self.create_slide_sample(index=0)
        slide2 = self.create_slide_sample(index=1)
        slide3 = self.create_slide_sample(index=2)

        created, tag1 = self.db_handler.create(Tags, **{
            'name': 'tag1',
            'owner_id': 'TEST_USER_ID'
        })
        assert created

        created, tag2 = self.db_handler.create(Tags, **{
            'name': 'tag2',
            'owner_id': 'TEST_USER_ID'
        })
        assert created

        created, tag3 = self.db_handler.create(Tags, **{
            'name': 'tag3',
            'owner_id': 'TEST_USER_ID'
        })
        assert created

        created, link1 = self.db_handler.create(SlideLinks, **{
            'slide_id': slide1.id,
            'tag_id': tag1.id,
            'value': 0,
        })
        assert created

        created, link2 = self.db_handler.create(SlideLinks, **{
            'slide_id': slide2.id,
            'tag_id': tag2.id,
            'value': 100,
        })
        assert created

        created, link3 = self.db_handler.create(SlideLinks, **{
            'slide_id': slide3.id,
            'tag_id': tag3.id,
            'value': None,
        })
        assert created

        links_and_tags = self.db_handler.get_links_and_tags(SlideLinks, 'TEST_USER_ID', (tag1.name, tag2.name, tag3.name))

        for slide in (slide1, slide2, slide3):
            found = False
            for link_tag in links_and_tags:
                if link_tag.SlideLinks.slide_id == slide.id:
                    found = True
                    break
            assert found


    def test_get_slide_thumb_by_index(self):
        user = self.create_test_user()
        pres = self.create_pres_sample()

        with open('files/slide_thumbnail_1.png', 'rb') as file:
            slide1 = self.create_slide_sample(index=0, thumbnail=file.read())

        with open('files/slide_thumbnail_2.png', 'rb') as file:
            slide2 = self.create_slide_sample(index=1, thumbnail=file.read())

        with open('files/slide_thumbnail_3.png', 'rb') as file:
            slide3 = self.create_slide_sample(index=2, thumbnail=file.read())

        slide_thumb_by_index_1 = self.db_handler.get_slide_thumb_by_index(user.id, pres.id, 2)
        with open('files/slide_thumbnail_3.png', 'rb') as file:
            assert slide_thumb_by_index_1 == file.read()

        slide_thumb_by_index_2 = self.db_handler.get_slide_thumb_by_index(user.id, pres.id, 1)
        with open('files/slide_thumbnail_2.png', 'rb') as file:
            assert slide_thumb_by_index_2 == file.read()

        slide_thumb_by_index_3 = self.db_handler.get_slide_thumb_by_index(user.id, pres.id, 0)
        with open('files/slide_thumbnail_1.png', 'rb') as file:
            assert slide_thumb_by_index_3 == file.read()

        none_slide_thumb = self.db_handler.get_slide_thumb_by_index('NOT_EXISTING_USER_ID', pres.id, 1)
        assert none_slide_thumb is None

        none_slide_thumb = self.db_handler.get_slide_thumb_by_index(user.id, 'NOT_EXISTING_PRESENTATION_ID', 1)
        assert none_slide_thumb is None


    def test_sync_folders(self):
        user = self.create_test_user()

        folder1 = {'id': 'TEST_FOLDER_1_ID','name': 'TEST_FOLDER_1_NAME'}
        folder2 = {'id': 'TEST_FOLDER_2_ID','name': 'TEST_FOLDER_2_NAME'}
        folder3 = {'id': 'TEST_FOLDER_3_ID','name': 'TEST_FOLDER_3_NAME'}

        actual_folders = [folder1, folder2, folder3]

        self.db_handler.sync_folders(user.id, actual_folders)
        db_folders = self.db_handler.findall(Folders, Folders.owner_id == user.id)

        for folder in actual_folders:
            found = False
            for db_folder in db_folders:
                if folder.get('id') == db_folder.id:
                    found = True
                    break
            assert found

        actual_folders = [folder2, folder3]

        self.db_handler.sync_folders(user.id, actual_folders)
        db_folders = self.db_handler.findall(Folders, Folders.owner_id == user.id)

        for folder in actual_folders:
            found = False
            for db_folder in db_folders:
                if folder.get('id') == db_folder.id:
                    found = True
                    break
            assert found

        for db_folder in db_folders:
            assert folder1.get('id') != db_folder.id

    def test_sync_presentations(self):
        user = self.create_test_user()

        presentation1 = {
            'id': 'TEST_PRESENTATION_1_ID',
            'name': 'TEST_PRESENTATION_1_NAME',
            'modifiedTime': '2023-05-01T00:00:00.0Z'
        }

        presentation2 = {
            'id': 'TEST_PRESENTATION_2_ID',
            'name': 'TEST_PRESENTATION_2_NAME',
            'modifiedTime': '2023-05-01T00:00:00.0Z'
        }

        presentation3 = {
            'id': 'TEST_PRESENTATION_3_ID',
            'name': 'TEST_PRESENTATION_3_NAME',
            'modifiedTime': '2023-05-01T00:00:00.0Z'
        }


        actual_presentations = [presentation1, presentation2, presentation3]

        synced, (created, modified) = self.db_handler.sync_presentations(user.id, actual_presentations)

        for pres in actual_presentations:
            found = False
            for created_pres in created:
                if pres.get('id') == created_pres.get('id'):
                    found = True
                    break
            assert found

        presentation2 = {
            'id': 'TEST_PRESENTATION_2_ID',
            'name': 'TEST_PRESENTATION_2_NAME',
            'modifiedTime': '2023-05-02T00:00:00.0Z'
        }
        actual_presentations = [presentation1, presentation2]

        synced, (created, modified) = self.db_handler.sync_presentations(user.id, actual_presentations)


        found = False
        for modified_pres in modified:
            if presentation2.get('id') == modified_pres.get('id'):
                found = True
                break
        assert found

        found = False
        for pres in synced:
            if presentation3.get('id') == pres.get('id'):
                found = True
                break
        assert not found

    def test_sync_presentation_slides(self):
        user = self.create_test_user()

        try:
            temp_path = os.path.join(SERVER_ROOT, 'presentation_processing/temp')
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)

            presentation1 = {
                'id': 'TEST_PRESENTATION_1_ID',
                'name': 'TEST_PRESENTATION_1_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            presentation2 = {
                'id': 'TEST_PRESENTATION_2_ID',
                'name': 'TEST_PRESENTATION_2_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            presentation3 = {
                'id': 'TEST_PRESENTATION_3_ID',
                'name': 'TEST_PRESENTATION_3_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            actual_presentations = [presentation1, presentation2, presentation3]
            synced, delta = self.db_handler.sync_presentations(user.id, actual_presentations)

            pres1_ratio = Slides.Ratio.STANDARD_4_TO_3
            pres1_text = ['SAMPLE TEXT 1']
            pres1_temp_path = os.path.join(temp_path, f'{presentation1.get("id")}')
            pres1_temp_images_path = os.path.join(pres1_temp_path, 'images')
            os.mkdir(pres1_temp_path)
            os.mkdir(pres1_temp_images_path)
            shutil.copyfile('files/slide_thumbnail_1.png', os.path.join(pres1_temp_images_path, 'Слайд1.png'))

            pres2_ratio = Slides.Ratio.STANDARD_4_TO_3
            pres2_text = ['SAMPLE TEXT 2']
            pres2_temp_path = os.path.join(temp_path, f'{presentation2.get("id")}')
            pres2_temp_images_path = os.path.join(pres2_temp_path, 'images')
            os.mkdir(os.path.join(pres2_temp_path))
            os.mkdir(pres2_temp_images_path)
            shutil.copyfile('files/slide_thumbnail_2.png', os.path.join(pres2_temp_images_path, 'Слайд1.png'))

            pres3_ratio = Slides.Ratio.STANDARD_4_TO_3
            pres3_text = ['SAMPLE TEXT 3']
            pres3_temp_path = os.path.join(temp_path, f'{presentation3.get("id")}')
            pres3_temp_images_path = os.path.join(pres3_temp_path, 'images')
            os.mkdir(os.path.join(pres3_temp_path))
            os.mkdir(pres3_temp_images_path)
            shutil.copyfile('files/slide_thumbnail_3.png', os.path.join(pres3_temp_images_path, 'Слайд1.png'))


            presentations_ratio = [pres1_ratio, pres2_ratio, pres3_ratio]
            presentations_text = [pres1_text, pres2_text, pres3_text]
            self.db_handler.sync_presentation_slides(synced, delta, presentations_ratio, presentations_text, user.id)

            slide1 = self.db_handler.find(Slides, Slides.pres_id == presentation1.get('id'))
            assert slide1 is not None
            assert slide1.text == 'SAMPLE TEXT 1'

            slide2 = self.db_handler.find(Slides, Slides.pres_id == presentation2.get('id'))
            assert slide2 is not None
            assert slide2.text == 'SAMPLE TEXT 2'

            slide3 = self.db_handler.find(Slides, Slides.pres_id == presentation3.get('id'))
            assert slide3 is not None
            assert slide3.text == 'SAMPLE TEXT 3'

            clear_temp()
            os.mkdir(temp_path)

            presentation2 = {
                'id': 'TEST_PRESENTATION_2_ID',
                'name': 'TEST_PRESENTATION_2_NAME',
                'modifiedTime': '2023-05-02T00:00:00.0Z'
            }

            actual_presentations = [presentation1, presentation2]
            synced, delta = self.db_handler.sync_presentations(user.id, actual_presentations)

            pres2_ratio = Slides.Ratio.STANDARD_4_TO_3
            pres2_text = ['UPDATED SAMPLE TEXT 2']
            pres2_temp_path = os.path.join(temp_path, f'{presentation2.get("id")}')
            pres2_temp_images_path = os.path.join(pres2_temp_path, 'images')
            os.mkdir(os.path.join(pres2_temp_path))
            os.mkdir(pres2_temp_images_path)
            shutil.copyfile('files/slide_thumbnail_4.png', os.path.join(pres2_temp_images_path, 'Слайд1.png'))
            shutil.copyfile('files/slide_thumbnail_2.png', os.path.join(pres2_temp_images_path, 'Слайд2.png'))

            presentations_ratio = [pres1_ratio, pres2_ratio]
            presentations_text = [pres1_text, pres2_text]
            self.db_handler.sync_presentation_slides(synced, delta, presentations_ratio, presentations_text, user.id)

            slide1 = self.db_handler.find(Slides, Slides.pres_id == presentation1.get('id'))
            assert slide1 is not None
            assert slide1.text == 'SAMPLE TEXT 1'

            pres_2_slides = self.db_handler.get_slides_index_asc(presentation2.get('id'))
            assert pres_2_slides is not None
            assert pres_2_slides[0].text == 'UPDATED SAMPLE TEXT 2'
            assert pres_2_slides[1].text == 'SAMPLE TEXT 2'


            slide3 = self.db_handler.find(Slides, Slides.pres_id == presentation3.get('id'))
            assert slide3 is None

        finally:
            clear_temp()

    def test_set_folder_mark(self):
        user = self.create_test_user()

        folder1 = {'id': 'TEST_FOLDER_1_ID', 'name': 'TEST_FOLDER_1_NAME'}

        actual_folders = [folder1]

        self.db_handler.sync_folders(user.id, actual_folders)

        folder = self.db_handler.find(Folders, Folders.id == folder1.get('id'))
        assert not folder.mark

        self.db_handler.set_folder_mark(user.id, folder.id, True)
        folder = self.db_handler.find(Folders, Folders.id == folder1.get('id'))
        assert folder.mark

        self.db_handler.set_folder_mark(user.id, folder.id, False)
        folder = self.db_handler.find(Folders, Folders.id == folder1.get('id'))
        assert not folder.mark

    def test_create_slide_link(self):
        user = self.create_test_user()

        self.create_pres_sample()
        slide = self.create_slide_sample()

        # Create Link
        self.db_handler.create_slide_link(slide.id, 'tag1', 100, user.id)

        slide_links = self.db_handler.findall(SlideLinks, SlideLinks.slide_id == slide.id)

        slide_link = None
        for link in slide_links:
            if link.slide_id == slide.id and link.value == 100:
                slide_link = link
                break
        assert slide_link is not None

        # Update Link
        self.db_handler.create_slide_link(slide.id, 'tag1', 200, user.id)
        slide_link = self.db_handler.read(SlideLinks, slide_link.id)

        assert slide_link is not None and slide_link.value == 200

    def test_remove_slide_link(self):
        user = self.create_test_user()

        self.create_pres_sample()
        slide = self.create_slide_sample()

        # Create Link
        self.db_handler.create_slide_link(slide.id, 'tag1', 100, user.id)

        slide_links = self.db_handler.findall(SlideLinks, SlideLinks.slide_id == slide.id)

        slide_link = None
        for link in slide_links:
            if link.slide_id == slide.id and link.value == 100:
                slide_link = link
                break
        assert slide_link is not None

        # Remove Link
        self.db_handler.remove_slide_link(slide.id, 'tag1', user.id)

        slide_link = self.db_handler.read(SlideLinks, slide_link.id)
        assert slide_link is None

    def test_get_slide_links(self):
        user = self.create_test_user()
        pres = self.create_pres_sample()
        slide = self.create_slide_sample()

        self.db_handler.create_slide_link(slide.id, 'tag1', 100, user.id)
        self.db_handler.create_slide_link(slide.id, 'tag2', 200, user.id)
        self.db_handler.create_slide_link(slide.id, 'tag3', 300, user.id)

        slide_links = self.db_handler.get_slide_links(slide.id, user.id)

        assert len(slide_links) == 3

        tag1 = self.db_handler.find(Tags, Tags.name == 'tag1', Tags.owner_id == user.id)
        tag2 = self.db_handler.find(Tags, Tags.name == 'tag2', Tags.owner_id == user.id)
        tag3 = self.db_handler.find(Tags, Tags.name == 'tag3', Tags.owner_id == user.id)


        found_slide_link1 = next((link for link in slide_links if
                                  link.get('slide_id') == slide.id and
                                  link.get('tag_id') == tag1.id and
                                  link.get('value') == 100), None)

        found_slide_link2 = next((link for link in slide_links if
                                  link.get('slide_id') == slide.id and
                                  link.get('tag_id') == tag2.id and
                                  link.get('value') == 200), None)

        found_slide_link3 = next((link for link in slide_links if
                                  link.get('slide_id') == slide.id and
                                  link.get('tag_id') == tag3.id and
                                  link.get('value') == 300), None)


        assert found_slide_link1 is not None
        assert found_slide_link2 is not None
        assert found_slide_link3 is not None

    def test_create_presentation_link(self):
        user = self.create_test_user()

        pres = self.create_pres_sample()

        # Create Link
        self.db_handler.create_presentation_link(pres.id, 'tag1', 100, user.id)

        pres_links = self.db_handler.findall(PresentationLinks, PresentationLinks.pres_id == pres.id)

        pres_link = None
        for link in pres_links:
            if link.pres_id == pres.id and link.value == 100:
                pres_link = link
                break
        assert pres_link is not None

        # Update Link
        self.db_handler.create_presentation_link(pres.id, 'tag1', 200, user.id)
        pres_link = self.db_handler.read(PresentationLinks, pres_link.id)

        assert pres_link is not None and pres_link.value == 200

    def test_remove_presentation_link(self):
        user = self.create_test_user()

        pres = self.create_pres_sample()

        # Create Link
        self.db_handler.create_presentation_link(pres.id, 'tag1', 100, user.id)

        pres_links = self.db_handler.findall(PresentationLinks, PresentationLinks.pres_id == pres.id)

        pres_link = None
        for link in pres_links:
            if link.pres_id == pres.id and link.value == 100:
                pres_link = link
                break
        assert pres_link is not None

        # Remove Link
        self.db_handler.remove_presentation_link(pres.id, 'tag1', user.id)

        pres_link = self.db_handler.read(PresentationLinks, pres_link.id)
        assert pres_link is None

    def test_get_presentation_links(self):
        user = self.create_test_user()
        pres = self.create_pres_sample()

        self.db_handler.create_presentation_link(pres.id, 'tag1', 100, user.id)
        self.db_handler.create_presentation_link(pres.id, 'tag2', 200, user.id)
        self.db_handler.create_presentation_link(pres.id, 'tag3', 300, user.id)

        pres_links = self.db_handler.get_presentation_links(pres.id, user.id)

        assert len(pres_links) == 3

        tag1 = self.db_handler.find(Tags, Tags.name == 'tag1', Tags.owner_id == user.id)
        tag2 = self.db_handler.find(Tags, Tags.name == 'tag2', Tags.owner_id == user.id)
        tag3 = self.db_handler.find(Tags, Tags.name == 'tag3', Tags.owner_id == user.id)

        found_pres_link1 = next((link for link in pres_links if
                                  link.get('presentation_id') == pres.id and
                                  link.get('tag_id') == tag1.id and
                                  link.get('value') == 100), None)

        found_pres_link2 = next((link for link in pres_links if
                                  link.get('presentation_id') == pres.id and
                                  link.get('tag_id') == tag2.id and
                                  link.get('value') == 200), None)

        found_pres_link3 = next((link for link in pres_links if
                                  link.get('presentation_id') == pres.id and
                                  link.get('tag_id') == tag3.id and
                                  link.get('value') == 300), None)

        assert found_pres_link1 is not None
        assert found_pres_link2 is not None
        assert found_pres_link3 is not None

    def test_get_presentations_by_tag_query(self):
        user = self.create_test_user()
        pres1 = self.create_pres_sample(id='TEST_PRESENTATION_1_ID')
        pres2 = self.create_pres_sample(id='TEST_PRESENTATION_2_ID')

        self.db_handler.create_presentation_link(pres1.id, 'tag1', 100, user.id)
        self.db_handler.create_presentation_link(pres1.id, 'tag2', None, user.id)

        self.db_handler.create_presentation_link(pres2.id, 'tag2', 100, user.id)
        self.db_handler.create_presentation_link(pres2.id, 'tag3', 200, user.id)

        found_presentations = self.db_handler.get_presentations_by_tag_query('tag1', user.id)
        assert len(found_presentations) == 1
        found_pres1 = next((pres for pres in found_presentations if pres.get('id') == pres1.id), None)
        assert found_pres1 is not None

        found_presentations = self.db_handler.get_presentations_by_tag_query('tag1 > 100', user.id)
        assert len(found_presentations) == 0

        found_presentations = self.db_handler.get_presentations_by_tag_query('tag2', user.id)
        assert len(found_presentations) == 2
        found_pres1 = next((pres for pres in found_presentations if pres.get('id') == pres1.id), None)
        assert found_pres1 is not None
        found_pres2 = next((pres for pres in found_presentations if pres.get('id') == pres2.id), None)
        assert found_pres2 is not None

        found_presentations = self.db_handler.get_presentations_by_tag_query('tag2 == 100', user.id)
        assert len(found_presentations) == 1
        found_pres2 = next((pres for pres in found_presentations if pres.get('id') == pres2.id), None)
        assert found_pres2 is not None

        found_presentations = self.db_handler.get_presentations_by_tag_query('tag3 <= 200', user.id)
        assert len(found_presentations) == 1
        found_pres2 = next((pres for pres in found_presentations if pres.get('id') == pres2.id), None)
        assert found_pres2 is not None

    def test_get_slides_by_tag_query(self):
        user = self.create_test_user()
        pres = self.create_pres_sample()

        slide1 = self.create_slide_sample(pres.id, index=0)
        slide2 = self.create_slide_sample(pres.id, index=1)

        self.db_handler.create_slide_link(slide1.id, 'tag1', 100, user.id)
        self.db_handler.create_slide_link(slide1.id, 'tag2', None, user.id)

        self.db_handler.create_slide_link(slide2.id, 'tag2', 100, user.id)
        self.db_handler.create_slide_link(slide2.id, 'tag3', 200, user.id)

        found_slides = self.db_handler.get_slides_by_tag_query('tag1', user.id)
        assert len(found_slides) == 1
        found_slide1 = next((slide for slide in found_slides if slide.id == slide1.id), None)
        assert found_slide1 is not None

        found_slides = self.db_handler.get_slides_by_tag_query('tag1 > 100', user.id)
        assert len(found_slides) == 0

        found_slides = self.db_handler.get_slides_by_tag_query('tag2', user.id)
        assert len(found_slides) == 2
        found_slide1 = next((slide for slide in found_slides if slide.id == slide1.id), None)
        assert found_slide1 is not None
        found_slide2 = next((slide for slide in found_slides if slide.id == slide2.id), None)
        assert found_slide2 is not None

        found_slides = self.db_handler.get_slides_by_tag_query('tag2 == 100', user.id)
        assert len(found_slides) == 1
        found_slide2 = next((slide for slide in found_slides if slide.id == slide2.id), None)
        assert found_slide2 is not None

        found_slides = self.db_handler.get_slides_by_tag_query('tag3 <= 200', user.id)
        assert len(found_slides) == 1
        found_slide2 = next((slide for slide in found_slides if slide.id == slide2.id), None)
        assert found_slide2 is not None

    def test_get_user_tag_list(self):
        user = self.create_test_user()
        pres = self.create_pres_sample()
        slide1 = self.create_slide_sample(index=0)
        slide2 = self.create_slide_sample(index=1)

        user_presentation_tags, user_slide_tags = self.db_handler.get_user_tags_list(user.id)
        assert len(user_presentation_tags) == 0
        assert len(user_slide_tags) == 0

        self.db_handler.create_presentation_link(pres.id, 'tag1', 100, user.id)
        self.db_handler.create_presentation_link(pres.id, 'tag2', 100, user.id)

        self.db_handler.create_slide_link(slide1.id, 'tag1', 100, user.id)
        self.db_handler.create_slide_link(slide1.id, 'tag2', 100, user.id)

        self.db_handler.create_slide_link(slide2.id, 'tag2', 100, user.id)
        self.db_handler.create_slide_link(slide2.id, 'tag3', 100, user.id)

        user_presentation_tags, user_slide_tags = self.db_handler.get_user_tags_list(user.id)
        assert len(user_presentation_tags) == 2
        assert len(user_slide_tags) == 3

        self.db_handler.remove_presentation_link(pres.id, 'tag1', user.id)

        self.db_handler.remove_slide_link(slide1.id, 'tag2', user.id)
        self.db_handler.remove_slide_link(slide2.id, 'tag3', user.id)

        user_presentation_tags, user_slide_tags = self.db_handler.get_user_tags_list(user.id)
        assert len(user_presentation_tags) == 1
        assert len(user_slide_tags) == 2

    def test_get_slides_by_filters(self):
        user = self.create_test_user()

        pres1 = self.create_pres_sample(id='TEST_PRESENTATION_1_ID')

        slide1_1 = self.create_slide_sample(pres_id=pres1.id, index=0, text='Hello',
                                            ratio=Slides.Ratio.STANDARD_4_TO_3)
        self.db_handler.create_slide_link(slide1_1.id, 'tag1', 100, user.id)

        slide1_2 = self.create_slide_sample(pres_id=pres1.id, index=0, text='world',
                                            ratio=Slides.Ratio.STANDARD_4_TO_3)
        self.db_handler.create_slide_link(slide1_2.id, 'tag2', None, user.id)

        pres2 = self.create_pres_sample(id='TEST_PRESENTATION_2_ID')

        slide2_1 = self.create_slide_sample(pres_id=pres2.id, index=0, text='foobar',
                                            ratio=Slides.Ratio.WIDESCREEN_16_TO_9)
        self.db_handler.create_slide_link(slide2_1.id, 'tag1', 200, user.id)

        slide2_2 = self.create_slide_sample(pres_id=pres2.id, index=0, text='Hello world',
                                            ratio=Slides.Ratio.WIDESCREEN_16_TO_9)
        self.db_handler.create_slide_link(slide2_2.id, 'tag3', None, user.id)

        found_slides = self.db_handler.get_slides_by_filters(
            presentations=[pres1, pres2],
            tag_query='',
            text_phrase='',
            ratio='auto',
            user_id=user.id
        )
        assert len(found_slides) == 4

        found_slides = self.db_handler.get_slides_by_filters(
            presentations=[pres1, pres2],
            tag_query='tag1',
            text_phrase='',
            ratio='auto',
            user_id=user.id
        )
        assert len(found_slides) == 2
        assert next((slide for slide in found_slides if slide.get('id') == slide1_1.id), None) is not None
        assert next((slide for slide in found_slides if slide.get('id') == slide2_1.id), None) is not None

        found_slides = self.db_handler.get_slides_by_filters(
            presentations=[pres1, pres2],
            tag_query='tag1 > 100',
            text_phrase='',
            ratio='auto',
            user_id=user.id
        )
        assert len(found_slides) == 1
        assert next((slide for slide in found_slides if slide.get('id') == slide2_1.id), None) is not None

        found_slides = self.db_handler.get_slides_by_filters(
            presentations=[pres1, pres2],
            tag_query='tag2 or tag3',
            text_phrase='',
            ratio='auto',
            user_id=user.id
        )
        assert len(found_slides) == 2
        assert next((slide for slide in found_slides if slide.get('id') == slide1_2.id), None) is not None
        assert next((slide for slide in found_slides if slide.get('id') == slide2_2.id), None) is not None

        found_slides = self.db_handler.get_slides_by_filters(
            presentations=[pres1, pres2],
            tag_query='',
            text_phrase='Hello',
            ratio='auto',
            user_id=user.id
        )
        assert len(found_slides) == 2
        assert next((slide for slide in found_slides if slide.get('id') == slide1_1.id), None) is not None
        assert next((slide for slide in found_slides if slide.get('id') == slide2_2.id), None) is not None

        found_slides = self.db_handler.get_slides_by_filters(
            presentations=[pres1],
            tag_query='',
            text_phrase='Hello',
            ratio='auto',
            user_id=user.id
        )
        assert len(found_slides) == 1
        assert next((slide for slide in found_slides if slide.get('id') == slide1_1.id), None) is not None

        found_slides = self.db_handler.get_slides_by_filters(
            presentations=[pres1, pres2],
            tag_query='',
            text_phrase='',
            ratio='widescreen_16_to_9',
            user_id=user.id
        )
        assert len(found_slides) == 2
        assert next((slide for slide in found_slides if slide.get('id') == slide2_1.id), None) is not None
        assert next((slide for slide in found_slides if slide.get('id') == slide2_2.id), None) is not None

        found_slides = self.db_handler.get_slides_by_filters(
            presentations=[pres1, pres2],
            tag_query='',
            text_phrase='',
            ratio='standard_4_to_3',
            user_id=user.id
        )
        assert len(found_slides) == 2
        assert next((slide for slide in found_slides if slide.get('id') == slide1_1.id), None) is not None
        assert next((slide for slide in found_slides if slide.get('id') == slide1_2.id), None) is not None

        found_slides = self.db_handler.get_slides_by_filters(
            presentations=[],
            tag_query='tag1',
            text_phrase='Hello',
            ratio='standard_4_to_3',
            user_id=user.id
        )
        assert len(found_slides) == 0

        found_slides = self.db_handler.get_slides_by_filters(
            presentations=[pres1, pres2],
            tag_query='INVALID_TAG_QUERY + 10 == "Hello"',
            text_phrase='Hello',
            ratio='standard_4_to_3',
            user_id=user.id
        )
        assert len(found_slides) == 0
        
    def test_pres_sync_uploaded(self):
        user = self.create_test_user()
        
        try:
            temp_path = os.path.join(SERVER_ROOT, 'presentation_processing/temp')
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)

            presentation1 = {
                'id': 'TEST_PRESENTATION_1_ID',
                'name': 'TEST_PRESENTATION_1_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            presentation2 = {
                'id': 'TEST_PRESENTATION_2_ID',
                'name': 'TEST_PRESENTATION_2_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            presentation3 = {
                'id': 'TEST_PRESENTATION_3_ID',
                'name': 'TEST_PRESENTATION_3_NAME',
                'modifiedTime': '2023-05-01T00:00:00.0Z'
            }

            actual_presentations = [presentation1, presentation2, presentation3]
            synced, delta = self.db_handler.sync_presentations(user.id, actual_presentations)
            
            with open('files/slide_thumbnail_1.png', 'rb') as file:
                slide1_thumb = file.read()
                
            slide1 = self.create_slide_sample(
                pres_id=presentation1.get('id'),
                index=0,
                text='SLIDE1',
                thumbnail=slide1_thumb
            )
            
            self.db_handler.create_slide_link(slide1.id, 'tag1', 100, user.id)


            with open('files/slide_thumbnail_2.png', 'rb') as file:
                slide2_thumb = file.read()

            slide2 = self.create_slide_sample(
                pres_id=presentation2.get('id'),
                index=0,
                text='SLIDE2',
                thumbnail=slide2_thumb
            )

            self.db_handler.create_slide_link(slide2.id, 'tag2', 200, user.id)
            
            with open('files/slide_thumbnail_3.png', 'rb') as file:
                slide3_thumb = file.read()

            slide3 = self.create_slide_sample(
                pres_id=presentation3.get('id'),
                index=0,
                text='SLIDE3',
                thumbnail=slide3_thumb
            )
            
            self.db_handler.create_slide_link(slide3.id, 'tag3', 300, user.id)

            pres = {
                'id': 'NEW_PRESENTATION_ID',
                'name': 'NEW_PRESENTATION_NAME',
                'modifiedTime': '2023-05-03T00:00:00.0Z'
            }
            
            pres_text = [slide1.text, slide2.text, slide3.text]
            pres_thumbs = [slide1.thumbnail, slide2.thumbnail, slide3.thumbnail]
            ratio = 'standard_4_to_3'
            slides_from = [slide1, slide2, slide3]
            
            self.db_handler.pres_sync_uploaded(pres, pres_text, pres_thumbs, ratio, slides_from, user.id)
            
            new_pres_from_db = self.db_handler.read(Presentations, pres.get('id'))
            assert new_pres_from_db is not None
            
            new_pres_slides = self.db_handler.get_slides_index_asc(new_pres_from_db.id)
            db_slide1 = new_pres_slides[0]
            db_slide2 = new_pres_slides[1]
            db_slide3 = new_pres_slides[2]
            
            assert slide1.text == db_slide1.text
            assert slide1.thumbnail == db_slide1.thumbnail
            
            slide1_links = self.db_handler.get_slide_links(slide1.id, user.id)
            db_slide1_links = self.db_handler.get_slide_links(db_slide1.id, user.id)
            
            for slide1_link in slide1_links:
                found = False
                for db_slide1_link in db_slide1_links:
                    if slide1_link.get('tag_id') == db_slide1_link.get('tag_id') and \
                            slide1_link.get('value') == db_slide1_link.get('value'):
                        found = True
                        break
                assert found

            assert slide2.text == db_slide2.text
            assert slide2.thumbnail == db_slide2.thumbnail

            slide2_links = self.db_handler.get_slide_links(slide2.id, user.id)
            db_slide2_links = self.db_handler.get_slide_links(db_slide2.id, user.id)

            for slide2_link in slide2_links:
                found = False
                for db_slide2_link in db_slide2_links:
                    if slide2_link.get('tag_id') == db_slide2_link.get('tag_id') and \
                            slide2_link.get('value') == db_slide2_link.get('value'):
                        found = True
                        break
                assert found

            assert slide3.text == db_slide3.text
            assert slide3.thumbnail == db_slide3.thumbnail

            slide3_links = self.db_handler.get_slide_links(slide3.id, user.id)
            db_slide3_links = self.db_handler.get_slide_links(db_slide3.id, user.id)

            for slide3_link in slide3_links:
                found = False
                for db_slide3_link in db_slide3_links:
                    if slide3_link.get('tag_id') == db_slide3_link.get('tag_id') and \
                            slide3_link.get('value') == db_slide3_link.get('value'):
                        found = True
                        break
                assert found

            
        finally:
            clear_temp()

    def test_migrate_tags(self):
        user = self.create_test_user()
        pres = self.create_pres_sample()

        slide1 = self.create_slide_sample(index=0)
        slide2 = self.create_slide_sample(index=1)

        self.db_handler.create_slide_link(slide1.id, 'tag1', 100, user.id)
        self.db_handler.create_slide_link(slide1.id, 'tag2', 200, user.id)

        tag1 = self.db_handler.find(Tags, Tags.name == 'tag1', Tags.owner_id == user.id)
        tag2 = self.db_handler.find(Tags, Tags.name == 'tag2', Tags.owner_id == user.id)

        found_links = self.db_handler.get_slide_links(slide2.id, user.id)
        assert len(found_links) == 0

        self.db_handler.migrate_tags(slide1, slide2)

        found_links = self.db_handler.get_slide_links(slide2.id, user.id)
        assert len(found_links) == 2
        assert next((link for link in found_links if link.get('tag_id') == tag1.id and link.get('value') == 100), None)
        assert next((link for link in found_links if link.get('tag_id') == tag2.id and link.get('value') == 200), None)

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
    def tearDownClass(cls):
        cls.db_handler.pool.close()

if __name__ == '__main__':
    unittest.main()