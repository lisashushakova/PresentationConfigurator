import os
import time
import unittest
from multiprocessing.pool import ThreadPool

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from app.definitions import db_user, db_password, db_url, db_name, ROOT
from app.server.main.database.database_handler import DatabaseHandler
from selenium_test_utils import do_login, do_logout, dummy_send


class SeleniumTests(unittest.TestCase):

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

    def test_folder_scenario(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get('http://localhost:3000')

        do_login(driver)

        app_header = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, 'AppHeader'))

        app_header_button_block = app_header.find_element(By.CLASS_NAME, 'button-block')

        buttons = app_header_button_block.find_elements(By.TAG_NAME, 'button')
        assert len(buttons) == 3

        user_settings_button = buttons[1]
        assert user_settings_button.accessible_name == 'Settings'

        WebDriverWait(driver, timeout=30).until(
            expected_conditions.element_to_be_clickable(user_settings_button)).click()

        user_folders = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        user_folders = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        assert len(user_folders) == 4

        folder1 = next((folder for folder in user_folders if folder.text == 'Папка 1'), None)
        assert folder1 is not None
        assert 'folder' in folder1.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder2 = next((folder for folder in user_folders if folder.text == 'Папка 2'), None)
        assert folder2 is not None
        assert 'folder' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder3 = next((folder for folder in user_folders if folder.text == 'Папка 3'), None)
        assert folder3 is not None
        assert 'folder' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')

        action_chains = ActionChains(driver)
        action_chains.context_click(folder2).perform()

        assert 'folder-full-pref' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder3.click()

        user_folders = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        assert len(user_folders) == 1

        folder4 = next((folder for folder in user_folders if folder.text == 'Папка 4'), None)
        assert folder4 is not None
        assert 'folder' in folder4.find_element(By.TAG_NAME, 'img').get_attribute('src')

        action_chains = ActionChains(driver)
        action_chains.context_click(folder4).perform()

        buttons = driver.find_elements(By.TAG_NAME, 'button')
        back_button = next((button for button in buttons if button.text == 'Назад'), None)
        assert back_button is not None

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(back_button)).click()

        user_folders = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        assert len(user_folders) == 4

        folder3 = next((folder for folder in user_folders if folder.text == 'Папка 3'), None)
        assert folder3 is not None
        assert 'folder-sub-pref' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder_preferences = WebDriverWait(driver, timeout=30)\
            .until(lambda d: d.find_element(By.CLASS_NAME, 'folder-preferences'))

        folder_preferences_header = folder_preferences.find_element(By.TAG_NAME, 'h3')
        refresh_button = folder_preferences_header.find_element(By.TAG_NAME, 'img')
        WebDriverWait(driver, timeout=30).until(expected_conditions.element_to_be_clickable(refresh_button)).click()

        user_folders = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        assert len(user_folders) == 4

        folder1 = next((folder for folder in user_folders if folder.text == 'Папка 1'), None)
        assert folder1 is not None
        assert 'folder' in folder1.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder2 = next((folder for folder in user_folders if folder.text == 'Папка 2'), None)
        assert folder2 is not None
        assert 'folder-full-pref' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder3 = next((folder for folder in user_folders if folder.text == 'Папка 3'), None)
        assert folder3 is not None
        assert 'folder-sub-pref' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')

        action_chains.move_to_element_with_offset(folder_preferences, 700, 0).click().perform()

        toolbar = WebDriverWait(driver, 30)\
            .until(lambda d: d.find_element(By.CLASS_NAME, 'toolbar'))

        select_presentation_button = toolbar.find_element(By.TAG_NAME, 'button')
        assert select_presentation_button.text == 'Открыть презентацию'

        action_chains.move_to_element(select_presentation_button).perform()

        select_presentation_menu = WebDriverWait(driver, 30)\
            .until(lambda d: d.find_element(By.CLASS_NAME, 'SelectPresentationMenu'))

        WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'pres-search'))

        folders = select_presentation_menu.find_elements(By.CLASS_NAME, 'folder')
        assert len(folders) == 3

        presentations = select_presentation_menu.find_elements(By.CLASS_NAME, 'presentation')
        assert len(presentations) == 2

        presentation2 = next((pres for pres in presentations if 'Презентация 2' in pres.text), None)
        assert presentation2 is not None

        presentation4 = next((pres for pres in presentations if 'Презентация 4' in pres.text), None)
        assert presentation4 is not None

        created = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'created'))

        for element in created:
            WebDriverWait(driver, 30).until(lambda d: 'default' in element.get_attribute('class'))

        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 2

        presentation2 = next((pres for pres in loaded_presentations if 'Презентация 2' in pres.text), None)
        assert presentation2 is not None


        presentation4 = next((pres for pres in loaded_presentations if 'Презентация 4' in pres.text), None)
        assert presentation4 is not None

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(presentation2)).click()

        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'SlideCard'))
        assert len(slides) == 3

        action_chains.move_to_element(select_presentation_button).perform()
        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))

        presentation4 = next((pres for pres in loaded_presentations if 'Презентация 4' in pres.text), None)
        assert presentation4 is not None

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(presentation4)).click()
        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'SlideCard'))
        assert len(slides) == 3

        do_logout(driver)

        coverage = driver.execute_script('return JSON.stringify(__coverage__)')
        with open(os.path.join(ROOT, f'client/coverage_raw/test_folder_coverage.json'), 'w') as file:
            file.write(coverage)

        driver.close()

    def test_tag_markup(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get('http://localhost:3000')

        do_login(driver)

        app_header = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, 'AppHeader'))

        app_header_button_block = app_header.find_element(By.CLASS_NAME, 'button-block')

        buttons = app_header_button_block.find_elements(By.TAG_NAME, 'button')
        assert len(buttons) == 3

        user_settings_button = buttons[1]
        assert user_settings_button.accessible_name == 'Settings'

        WebDriverWait(driver, timeout=30).until(
            expected_conditions.element_to_be_clickable(user_settings_button)).click()

        user_folders = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        assert len(user_folders) == 4

        folder1 = next((folder for folder in user_folders if folder.text == 'Папка 1'), None)
        assert folder1 is not None
        assert 'folder' in folder1.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder2 = next((folder for folder in user_folders if folder.text == 'Папка 2'), None)
        assert folder2 is not None
        assert 'folder' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder3 = next((folder for folder in user_folders if folder.text == 'Папка 3'), None)
        assert folder3 is not None
        assert 'folder' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')

        action_chains = ActionChains(driver)
        action_chains.context_click(folder1).perform()
        action_chains.context_click(folder2).perform()
        action_chains.context_click(folder3).perform()

        assert 'folder-full-pref' in folder1.find_element(By.TAG_NAME, 'img').get_attribute('src')
        assert 'folder-full-pref' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')
        assert 'folder-full-pref' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')


        folder_preferences = WebDriverWait(driver, timeout=30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'folder-preferences'))

        action_chains.move_to_element_with_offset(folder_preferences, 700, 0).click().perform()

        toolbar = WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'toolbar'))

        select_presentation_button = toolbar.find_element(By.TAG_NAME, 'button')
        assert select_presentation_button.text == 'Открыть презентацию'

        action_chains.move_to_element(select_presentation_button).perform()

        select_presentation_menu = WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'SelectPresentationMenu'))

        WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'pres-search'))

        folders = select_presentation_menu.find_elements(By.CLASS_NAME, 'folder')
        assert len(folders) == 4


        created = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'created'))

        for element in created:
            WebDriverWait(driver, 30).until(lambda d: 'default' in element.get_attribute('class'))

        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 4

        presentation1 = next((pres for pres in loaded_presentations if 'Презентация 1' in pres.text), None)
        assert presentation1 is not None

        presentation2 = next((pres for pres in loaded_presentations if 'Презентация 2' in pres.text), None)
        assert presentation2 is not None

        presentation3 = next((pres for pres in loaded_presentations if 'Презентация 3' in pres.text), None)
        assert presentation3 is not None

        presentation4 = next((pres for pres in loaded_presentations if 'Презентация 4' in pres.text), None)
        assert presentation4 is not None

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(presentation1)).click()

        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'SlideCard'))
        assert len(slides) == 3

        slides[0].click()

        tag_table = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'TagTable'))
        assert tag_table is not None
        tag_table_create_row = driver.find_element(By.CLASS_NAME, 'TableCreateTagRow')
        assert tag_table_create_row is not None
        inputs = tag_table_create_row.find_elements(By.TAG_NAME, 'input')
        assert len(inputs) == 2
        create_tag_name = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == 'tag'))
        assert create_tag_name is not None
        create_tag_value = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == '100'))
        assert create_tag_value is not None

        create_tag_name.send_keys('tag1')
        create_tag_value.send_keys('200')

        create_tag_button = WebDriverWait(driver, 1).until(
            lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))
        assert create_tag_button is not None

        create_tag_value.send_keys(Keys.CONTROL + "a")
        create_tag_value.send_keys(Keys.BACKSPACE)
        create_tag_value.send_keys(Keys.CONTROL + "a")
        create_tag_value.send_keys(Keys.BACKSPACE)
        create_tag_value.send_keys('ABCDEF')

        with self.assertRaises(TimeoutException):
            WebDriverWait(driver, 1).until(
                lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))

        create_tag_value.send_keys(Keys.CONTROL + "a")
        create_tag_value.send_keys(Keys.BACKSPACE)

        create_tag_button = WebDriverWait(driver, 1).until(
            lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))
        assert create_tag_button is not None

        create_tag_name.send_keys(Keys.CONTROL + "a")
        create_tag_name.send_keys(Keys.BACKSPACE)

        create_tag_name.send_keys('100')

        with self.assertRaises(TimeoutException):
            WebDriverWait(driver, 1).until(
                lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))

        create_tag_name.send_keys(Keys.CONTROL + "a")
        create_tag_name.send_keys(Keys.BACKSPACE)

        create_tag_value.send_keys(Keys.CONTROL + "a")
        create_tag_value.send_keys(Keys.BACKSPACE)

        create_tag_name.send_keys('tag1')
        create_tag_value.send_keys('100')

        create_tag_button = WebDriverWait(driver, 1).until(
            lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))
        assert create_tag_button is not None

        create_tag_button.click()

        tag_table_row = WebDriverWait(driver, 30).until(
            lambda d: tag_table.find_element(By.CLASS_NAME, 'TableRow'))

        tag_name = tag_table_row.find_element(By.TAG_NAME, 'div')
        assert tag_name.text == 'tag1'

        tag_value = tag_table_row.find_element(By.TAG_NAME, 'input')
        assert tag_value.get_attribute('value') == '100'

        tag_button_img = tag_table_row.find_element(By.TAG_NAME, 'img')
        assert 'cross-red' in tag_button_img.get_attribute('src')

        tag_value.send_keys(Keys.CONTROL + "a")
        tag_value.send_keys(Keys.BACKSPACE)

        assert 'check-green' in tag_button_img.get_attribute('src')

        tag_value.send_keys('ABCDEF')

        assert 'cross-red' in tag_button_img.get_attribute('src')

        app_header.click()

        assert tag_value.get_attribute('value') == '100'

        tag_value.send_keys(Keys.CONTROL + "a")
        tag_value.send_keys(Keys.BACKSPACE)

        assert 'check-green' in tag_button_img.get_attribute('src')

        tag_button_img.click()

        assert 'cross-red' in tag_button_img.get_attribute('src')

        tag_button_img.click()

        with self.assertRaises(TimeoutException):
            WebDriverWait(driver, 1).until(
                lambda d: tag_table_create_row.find_element(By.CLASS_NAME, 'TableRow'))

        create_tag_name.send_keys('tag1')
        create_tag_value.send_keys('100')
        create_tag_button.click()

        create_tag_name.send_keys('tag2')
        create_tag_value.send_keys('200')
        create_tag_button.click()

        create_tag_name.send_keys('tag3')
        create_tag_value.send_keys('300')
        create_tag_button.click()

        slides[1].click()

        tag_table = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'TagTable'))
        assert tag_table is not None
        tag_table_create_row = driver.find_element(By.CLASS_NAME, 'TableCreateTagRow')
        assert tag_table_create_row is not None
        inputs = tag_table_create_row.find_elements(By.TAG_NAME, 'input')
        assert len(inputs) == 2
        create_tag_name = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == 'tag'))
        assert create_tag_name is not None
        create_tag_value = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == '100'))
        assert create_tag_value is not None

        create_tag_name.send_keys('tag4')
        create_tag_value.send_keys('100')
        create_tag_button.click()

        create_tag_name.send_keys('tag5')
        create_tag_value.send_keys('200')
        create_tag_button.click()

        create_tag_name.send_keys('tag6')
        create_tag_value.send_keys('300')
        create_tag_button.click()

        slides[0].click()

        tags = WebDriverWait(driver, 5).until(
            lambda d: d.find_elements(By.CLASS_NAME, 'TableRow'))
        assert len(tags) == 3

        slides[1].click()

        tags = WebDriverWait(driver, 5).until(
            lambda d: d.find_elements(By.CLASS_NAME, 'TableRow'))
        assert len(tags) == 3

        toolbar_buttons = toolbar.find_elements(By.TAG_NAME, 'button')
        presentation_tags_button = next((btn for btn in toolbar_buttons if btn.text == 'Теги презентации'), None)
        assert presentation_tags_button is not None

        presentation_tags_button.click()

        presentation_tags_modal = WebDriverWait(driver, 30).until(
            lambda d: d.find_element(By.CLASS_NAME, 'PresentationTagsModal'))

        tag_table = WebDriverWait(driver, 30).until(
            lambda d: presentation_tags_modal.find_element(By.CLASS_NAME, 'TagTable'))
        assert tag_table is not None
        tag_table_create_row = tag_table.find_element(By.CLASS_NAME, 'TableCreateTagRow')
        assert tag_table_create_row is not None
        inputs = tag_table_create_row.find_elements(By.TAG_NAME, 'input')
        assert len(inputs) == 2
        create_tag_name = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == 'tag'))
        assert create_tag_name is not None
        create_tag_value = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == '100'))
        assert create_tag_value is not None

        create_tag_name.send_keys('tag1')
        create_tag_value.send_keys('100')

        create_tag_button = WebDriverWait(driver, 1).until(
            lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))
        assert create_tag_button is not None

        create_tag_button.click()

        create_tag_name.send_keys('tag2')
        create_tag_value.send_keys('200')

        create_tag_button = WebDriverWait(driver, 1).until(
            lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))
        assert create_tag_button is not None

        create_tag_button.click()

        create_tag_name.send_keys('tag3')
        create_tag_value.send_keys('300')

        create_tag_button = WebDriverWait(driver, 1).until(
            lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))
        assert create_tag_button is not None

        create_tag_button.click()

        presentation_tags = WebDriverWait(driver, timeout=30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'presentation-tags'))
        action_chains.move_to_element_with_offset(presentation_tags, 700, 0).click().perform()

        user_tags_button = buttons[0]
        assert user_tags_button.accessible_name == 'Tags'

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(user_tags_button)).click()

        columns = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'column'))
        pres_column = columns[0]
        assert 'Презентации' in pres_column.text

        WebDriverWait(driver, 30).until(lambda d: pres_column.find_elements(By.TAG_NAME, 'div'))

        assert 'tag1' in pres_column.text
        assert 'tag2' in pres_column.text
        assert 'tag3' in pres_column.text

        slide_column = columns[1]
        assert 'Слайды' in slide_column.text

        assert 'tag1' in slide_column.text
        assert 'tag2' in slide_column.text
        assert 'tag3' in slide_column.text
        assert 'tag4' in slide_column.text
        assert 'tag5' in slide_column.text
        assert 'tag6' in slide_column.text

        user_tags = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'user-tags'))
        user_tags.click()
        assert driver.find_element(By.CLASS_NAME, 'user-tags') is not None
        action_chains.move_to_element_with_offset(user_tags, 700, 0).click().perform()

        coverage = driver.execute_script('return JSON.stringify(__coverage__)')
        with open(os.path.join(ROOT, f'client/coverage_raw/test_tag_markup_coverage.json'), 'w') as file:
            file.write(coverage)

        driver.close()

    def test_pres_search(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get('http://localhost:3000')

        do_login(driver)

        app_header = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, 'AppHeader'))

        app_header_button_block = app_header.find_element(By.CLASS_NAME, 'button-block')

        buttons = app_header_button_block.find_elements(By.TAG_NAME, 'button')
        assert len(buttons) == 3

        user_settings_button = buttons[1]
        assert user_settings_button.accessible_name == 'Settings'

        WebDriverWait(driver, timeout=30).until(
            expected_conditions.element_to_be_clickable(user_settings_button)).click()

        user_folders = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        assert len(user_folders) == 4

        folder1 = next((folder for folder in user_folders if folder.text == 'Папка 1'), None)
        assert folder1 is not None
        assert 'folder' in folder1.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder2 = next((folder for folder in user_folders if folder.text == 'Папка 2'), None)
        assert folder2 is not None
        assert 'folder' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder3 = next((folder for folder in user_folders if folder.text == 'Папка 3'), None)
        assert folder3 is not None
        assert 'folder' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')

        action_chains = ActionChains(driver)
        action_chains.context_click(folder1).perform()
        action_chains.context_click(folder2).perform()
        action_chains.context_click(folder3).perform()

        time.sleep(0.5)

        assert 'folder-full-pref' in folder1.find_element(By.TAG_NAME, 'img').get_attribute('src')
        assert 'folder-full-pref' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')
        assert 'folder-full-pref' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')


        folder_preferences = WebDriverWait(driver, timeout=30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'folder-preferences'))

        action_chains.move_to_element_with_offset(folder_preferences, 700, 0).click().perform()

        toolbar = WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'toolbar'))

        select_presentation_button = toolbar.find_element(By.TAG_NAME, 'button')
        assert select_presentation_button.text == 'Открыть презентацию'

        action_chains.move_to_element(select_presentation_button).perform()

        select_presentation_menu = WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'SelectPresentationMenu'))

        WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'pres-search'))

        folders = select_presentation_menu.find_elements(By.CLASS_NAME, 'folder')
        assert len(folders) == 4


        created = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'created'))

        for element in created:
            WebDriverWait(driver, 30).until(lambda d: 'default' in element.get_attribute('class'))

        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 4

        presentation1 = next((pres for pres in loaded_presentations if 'Презентация 1' in pres.text), None)
        assert presentation1 is not None

        presentation2 = next((pres for pres in loaded_presentations if 'Презентация 2' in pres.text), None)
        assert presentation2 is not None

        presentation3 = next((pres for pres in loaded_presentations if 'Презентация 3' in pres.text), None)
        assert presentation3 is not None

        presentation4 = next((pres for pres in loaded_presentations if 'Презентация 4' in pres.text), None)
        assert presentation4 is not None

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(presentation1)).click()

        toolbar_buttons = toolbar.find_elements(By.TAG_NAME, 'button')
        presentation_tags_button = next((btn for btn in toolbar_buttons if btn.text == 'Теги презентации'), None)
        assert presentation_tags_button is not None

        presentation_tags_button.click()

        presentation_tags_modal = WebDriverWait(driver, 30).until(
            lambda d: d.find_element(By.CLASS_NAME, 'PresentationTagsModal'))

        tag_table = WebDriverWait(driver, 30).until(
            lambda d: presentation_tags_modal.find_element(By.CLASS_NAME, 'TagTable'))
        assert tag_table is not None
        tag_table_create_row = tag_table.find_element(By.CLASS_NAME, 'TableCreateTagRow')
        assert tag_table_create_row is not None
        inputs = tag_table_create_row.find_elements(By.TAG_NAME, 'input')
        assert len(inputs) == 2
        create_tag_name = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == 'tag'))
        assert create_tag_name is not None
        create_tag_value = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == '100'))
        assert create_tag_value is not None

        create_tag_name.send_keys('tag1')
        create_tag_value.send_keys('100')


        create_tag_button = WebDriverWait(driver, 1).until(
            lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))
        assert create_tag_button is not None

        create_tag_button.click()

        presentation_tags = WebDriverWait(driver, timeout=30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'presentation-tags'))
        action_chains.move_to_element_with_offset(presentation_tags, 700, 0).click().perform()

        action_chains.move_to_element(select_presentation_button).perform()
        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))

        presentation4 = next((pres for pres in loaded_presentations if 'Презентация 4' in pres.text), None)
        assert presentation4 is not None

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(presentation4)).click()

        toolbar_buttons = toolbar.find_elements(By.TAG_NAME, 'button')
        presentation_tags_button = next((btn for btn in toolbar_buttons if btn.text == 'Теги презентации'), None)
        assert presentation_tags_button is not None

        presentation_tags_button.click()

        presentation_tags_modal = WebDriverWait(driver, 30).until(
            lambda d: d.find_element(By.CLASS_NAME, 'PresentationTagsModal'))

        tag_table = WebDriverWait(driver, 30).until(
            lambda d: presentation_tags_modal.find_element(By.CLASS_NAME, 'TagTable'))
        assert tag_table is not None
        tag_table_create_row = tag_table.find_element(By.CLASS_NAME, 'TableCreateTagRow')
        assert tag_table_create_row is not None
        inputs = tag_table_create_row.find_elements(By.TAG_NAME, 'input')
        assert len(inputs) == 2
        create_tag_name = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == 'tag'))
        assert create_tag_name is not None
        create_tag_value = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == '100'))
        assert create_tag_value is not None

        create_tag_name.send_keys('tag1')
        create_tag_value.send_keys('200')

        create_tag_button = WebDriverWait(driver, 1).until(
            lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))
        assert create_tag_button is not None

        create_tag_button.click()

        presentation_tags = WebDriverWait(driver, timeout=30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'presentation-tags'))
        action_chains.move_to_element_with_offset(presentation_tags, 700, 0).click().perform()

        action_chains.move_to_element(select_presentation_button).perform()

        pres_search = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'pres-search'))
        pres_search_input = pres_search.find_element(By.TAG_NAME, 'input')

        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 4

        pres_search_input.send_keys('Презентация')

        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 4

        pres_search_input.send_keys(Keys.CONTROL + "a")
        pres_search_input.send_keys(Keys.BACKSPACE)
        pres_search_input.send_keys('Презентация 1')

        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 1

        pres_search_input.send_keys(Keys.CONTROL + "a")
        pres_search_input.send_keys(Keys.BACKSPACE)
        pres_search_input.send_keys('презентация')

        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 4

        WebDriverWait(driver, 30).until(lambda d: d.find_element(By.ID, 'pres-search-tags')).click()

        pres_search_input.send_keys(Keys.CONTROL + "a")
        pres_search_input.send_keys(Keys.BACKSPACE)
        dummy_send(pres_search_input, 'tag1', 0.1)
        pres_search_input.send_keys(Keys.ENTER)

        loaded_presentations = WebDriverWait(driver, 5).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 2

        pres_search_input.send_keys(Keys.CONTROL + "a")
        pres_search_input.send_keys(Keys.BACKSPACE)
        dummy_send(pres_search_input, 'tag1 > 50', 0.1)
        pres_search_input.send_keys(Keys.ENTER)

        loaded_presentations = WebDriverWait(driver, 5).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 2


        pres_search_input.send_keys(Keys.CONTROL + "a")
        pres_search_input.send_keys(Keys.BACKSPACE)
        dummy_send(pres_search_input, 'tag1 > 100', 0.1)
        pres_search_input.send_keys(Keys.ENTER)

        loaded_presentations = WebDriverWait(driver, 5).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 1

        pres_search_input.send_keys(Keys.CONTROL + "a")
        pres_search_input.send_keys(Keys.BACKSPACE)
        dummy_send(pres_search_input, 'tag1 > 200', 0.1)
        pres_search_input.send_keys(Keys.ENTER)

        with self.assertRaises(TimeoutException):
            WebDriverWait(driver, 5).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))

        coverage = driver.execute_script('return JSON.stringify(__coverage__)')
        with open(os.path.join(ROOT, f'client/coverage_raw/test_pres_search_coverage.json'), 'w') as file:
            file.write(coverage)


        driver.close()

    def test_import_slides(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get('http://localhost:3000')

        do_login(driver)

        app_header = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, 'AppHeader'))

        app_header_button_block = app_header.find_element(By.CLASS_NAME, 'button-block')

        buttons = app_header_button_block.find_elements(By.TAG_NAME, 'button')
        assert len(buttons) == 3

        user_settings_button = buttons[1]
        assert user_settings_button.accessible_name == 'Settings'

        WebDriverWait(driver, timeout=30).until(
            expected_conditions.element_to_be_clickable(user_settings_button)).click()

        user_folders = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        assert len(user_folders) == 4

        folder1 = next((folder for folder in user_folders if folder.text == 'Папка 1'), None)
        assert folder1 is not None
        assert 'folder' in folder1.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder2 = next((folder for folder in user_folders if folder.text == 'Папка 2'), None)
        assert folder2 is not None
        assert 'folder' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder3 = next((folder for folder in user_folders if folder.text == 'Папка 3'), None)
        assert folder3 is not None
        assert 'folder' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')

        action_chains = ActionChains(driver)
        action_chains.context_click(folder1).perform()
        action_chains.context_click(folder2).perform()
        action_chains.context_click(folder3).perform()

        assert 'folder-full-pref' in folder1.find_element(By.TAG_NAME, 'img').get_attribute('src')
        assert 'folder-full-pref' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')
        assert 'folder-full-pref' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder_preferences = WebDriverWait(driver, timeout=30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'folder-preferences'))

        action_chains.move_to_element_with_offset(folder_preferences, 700, 0).click().perform()

        toolbar = WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'toolbar'))

        select_presentation_button = toolbar.find_element(By.TAG_NAME, 'button')
        assert select_presentation_button.text == 'Открыть презентацию'

        action_chains.move_to_element(select_presentation_button).perform()

        select_presentation_menu = WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'SelectPresentationMenu'))

        WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'pres-search'))

        folders = select_presentation_menu.find_elements(By.CLASS_NAME, 'folder')
        assert len(folders) == 4


        created = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'created'))

        for element in created:
            WebDriverWait(driver, 30).until(lambda d: 'default' in element.get_attribute('class'))

        time.sleep(2)

        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 4

        presentation1 = next((pres for pres in loaded_presentations if 'Презентация 1' in pres.text), None)
        assert presentation1 is not None

        presentation2 = next((pres for pres in loaded_presentations if 'Презентация 2' in pres.text), None)
        assert presentation2 is not None

        presentation3 = next((pres for pres in loaded_presentations if 'Презентация 3' in pres.text), None)
        assert presentation3 is not None

        presentation4 = next((pres for pres in loaded_presentations if 'Презентация 4' in pres.text), None)
        assert presentation4 is not None

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(presentation1)).click()

        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'SlideCard'))
        assert len(slides) == 3

        slides[0].click()

        tag_table = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'TagTable'))
        assert tag_table is not None
        tag_table_create_row = driver.find_element(By.CLASS_NAME, 'TableCreateTagRow')
        assert tag_table_create_row is not None
        inputs = tag_table_create_row.find_elements(By.TAG_NAME, 'input')
        assert len(inputs) == 2
        create_tag_name = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == 'tag'))
        assert create_tag_name is not None
        create_tag_value = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == '100'))
        assert create_tag_value is not None

        create_tag_name.send_keys('tag1')
        create_tag_value.send_keys('100')

        create_tag_button = WebDriverWait(driver, 1).until(
            lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))
        assert create_tag_button is not None

        create_tag_button.click()

        slides[1].click()

        tag_table = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'TagTable'))
        assert tag_table is not None
        tag_table_create_row = driver.find_element(By.CLASS_NAME, 'TableCreateTagRow')
        assert tag_table_create_row is not None
        inputs = tag_table_create_row.find_elements(By.TAG_NAME, 'input')
        assert len(inputs) == 2
        create_tag_name = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == 'tag'))
        assert create_tag_name is not None
        create_tag_value = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == '100'))
        assert create_tag_value is not None

        create_tag_name.send_keys('tag2')
        create_tag_value.send_keys('200')
        create_tag_button.click()

        action_chains.move_to_element(select_presentation_button).perform()

        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 4

        presentation2 = next((pres for pres in loaded_presentations if 'Презентация 2' in pres.text), None)
        assert presentation2 is not None

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(presentation2)).click()

        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'SlideCard'))
        assert len(slides) == 3

        time.sleep(0.1)

        slides[0].click()

        tag_table = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'TagTable'))
        assert tag_table is not None
        tag_table_create_row = driver.find_element(By.CLASS_NAME, 'TableCreateTagRow')
        assert tag_table_create_row is not None
        inputs = tag_table_create_row.find_elements(By.TAG_NAME, 'input')
        assert len(inputs) == 2
        create_tag_name = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == 'tag'))
        assert create_tag_name is not None
        create_tag_value = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == '100'))
        assert create_tag_value is not None

        create_tag_name.send_keys('tag1')
        create_tag_value.send_keys('300')

        create_tag_button = WebDriverWait(driver, 1).until(
            lambda d: tag_table_create_row.find_element(By.TAG_NAME, 'button'))
        assert create_tag_button is not None

        create_tag_button.click()

        slides[1].click()

        tag_table = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'TagTable'))
        assert tag_table is not None
        tag_table_create_row = driver.find_element(By.CLASS_NAME, 'TableCreateTagRow')
        assert tag_table_create_row is not None
        inputs = tag_table_create_row.find_elements(By.TAG_NAME, 'input')
        assert len(inputs) == 2
        create_tag_name = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == 'tag'))
        assert create_tag_name is not None
        create_tag_value = next((inpt for inpt in inputs if inpt.get_attribute('placeholder') == '100'))
        assert create_tag_value is not None

        create_tag_name.send_keys('tag2')
        create_tag_value.send_keys('400')
        create_tag_button.click()

        app_sidebar = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'AppSidebar'))
        sidebar_buttons = app_sidebar.find_elements(By.TAG_NAME, 'button')

        tag_markup_button = sidebar_buttons[0]
        assert tag_markup_button.text == 'Разметка тегов'

        build_presentation_button = sidebar_buttons[1]
        assert build_presentation_button.text == 'Сборка презентации'

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(build_presentation_button)).click()
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(tag_markup_button)).click()
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(build_presentation_button)).click()

        toolbar = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'toolbar'))

        import_slides_button = toolbar.find_element(By.TAG_NAME, 'button')
        assert import_slides_button.text == 'Импорт слайдов'

        import_slides_button.click()

        import_slides = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'import-slides'))
        buttons = import_slides.find_elements(By.TAG_NAME, 'button')

        presentation_filter = WebDriverWait(driver, 30).until(lambda d: import_slides.find_element(By.CLASS_NAME, 'presentation-filter'))
        presentation_filter_inputs = presentation_filter.find_elements(By.TAG_NAME, 'input')
        presentation_filter_button = buttons[0]
        assert presentation_filter_button.text == 'Снять выделение'

        import_button = buttons[1]
        assert import_button.text == 'Импорт слайдов'

        assert all([inpt.get_attribute('selected') == 'true' for inpt in presentation_filter_inputs])

        presentation_filter_button.click()

        assert not any([inpt.get_attribute('selected') == 'true' for inpt in presentation_filter_inputs])

        presentation_filter_inputs[0].click()
        presentation_filter_inputs[0].click()
        presentation_filter_inputs[0].click()
        presentation_filter_inputs[1].click()

        import_button.click()
        time.sleep(0.2)

        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'PoolSlideCard'))
        assert len(slides) == 6

        import_slides_button.click()

        import_slides = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'import-slides'))
        buttons = import_slides.find_elements(By.TAG_NAME, 'button')

        presentation_filter_button = buttons[0]
        assert presentation_filter_button.text == 'Снять выделение'

        tag_filter = WebDriverWait(driver, 30).until(lambda d: import_slides.find_element(By.CLASS_NAME, 'tag-filter'))
        tag_filter_input = tag_filter.find_element(By.TAG_NAME, 'input')

        import_button = buttons[1]
        assert import_button.text == 'Импорт слайдов'

        tag_filter_input.send_keys('tag1 or tag2 < 300')

        import_button.click()
        time.sleep(1)

        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'PoolSlideCard'))
        assert len(slides) == 3

        import_slides_button.click()

        import_slides = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'import-slides'))
        buttons = import_slides.find_elements(By.TAG_NAME, 'button')

        presentation_filter_button = buttons[0]
        assert presentation_filter_button.text == 'Снять выделение'
        text_filter = WebDriverWait(driver, 30).until(
            lambda d: import_slides.find_element(By.CLASS_NAME, 'text-filter'))
        text_filter_input = text_filter.find_element(By.TAG_NAME, 'input')

        import_button = buttons[1]
        assert import_button.text == 'Импорт слайдов'

        text_filter_input.send_keys('Презентация')
        import_button.click()
        time.sleep(0.2)

        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'PoolSlideCard'))
        assert len(slides) == 4

        import_slides_button.click()

        import_slides = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'import-slides'))
        buttons = import_slides.find_elements(By.TAG_NAME, 'button')

        presentation_filter_button = buttons[0]
        assert presentation_filter_button.text == 'Снять выделение'

        ratio_filter = WebDriverWait(driver, 30).until(
            lambda d: import_slides.find_element(By.CLASS_NAME, 'ratio-filter'))
        ratio_filter_inputs = ratio_filter.find_elements(By.TAG_NAME, 'input')

        import_button = buttons[1]
        assert import_button.text == 'Импорт слайдов'

        ratio_filter_inputs[2].click()
        import_button.click()
        time.sleep(0.2)

        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'PoolSlideCard'))
        assert len(slides) == 3

        coverage = driver.execute_script('return JSON.stringify(__coverage__)')
        with open(os.path.join(ROOT, f'client/coverage_raw/test_import_slides_coverage.json'), 'w') as file:
            file.write(coverage)

        driver.close()

    def test_build_presentation(self):

        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get('http://localhost:3000')

        do_login(driver)

        app_header = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, 'AppHeader'))

        app_header_button_block = app_header.find_element(By.CLASS_NAME, 'button-block')

        buttons = app_header_button_block.find_elements(By.TAG_NAME, 'button')
        assert len(buttons) == 3

        user_settings_button = buttons[1]
        assert user_settings_button.accessible_name == 'Settings'

        WebDriverWait(driver, timeout=30).until(
            expected_conditions.element_to_be_clickable(user_settings_button)).click()

        user_folders = WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        assert len(user_folders) == 4

        folder1 = next((folder for folder in user_folders if folder.text == 'Папка 1'), None)
        assert folder1 is not None
        assert 'folder' in folder1.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder2 = next((folder for folder in user_folders if folder.text == 'Папка 2'), None)
        assert folder2 is not None
        assert 'folder' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder3 = next((folder for folder in user_folders if folder.text == 'Папка 3'), None)
        assert folder3 is not None
        assert 'folder' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')

        action_chains = ActionChains(driver)
        action_chains.context_click(folder1).perform()
        action_chains.context_click(folder2).perform()
        action_chains.context_click(folder3).perform()

        assert 'folder-full-pref' in folder1.find_element(By.TAG_NAME, 'img').get_attribute('src')
        assert 'folder-full-pref' in folder2.find_element(By.TAG_NAME, 'img').get_attribute('src')
        assert 'folder-full-pref' in folder3.find_element(By.TAG_NAME, 'img').get_attribute('src')

        folder_preferences = WebDriverWait(driver, timeout=30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'folder-preferences'))

        action_chains.move_to_element_with_offset(folder_preferences, 700, 0).click().perform()

        toolbar = WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'toolbar'))

        select_presentation_button = toolbar.find_element(By.TAG_NAME, 'button')
        assert select_presentation_button.text == 'Открыть презентацию'

        action_chains.move_to_element(select_presentation_button).perform()

        select_presentation_menu = WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'SelectPresentationMenu'))

        WebDriverWait(driver, 30) \
            .until(lambda d: d.find_element(By.CLASS_NAME, 'pres-search'))

        folders = select_presentation_menu.find_elements(By.CLASS_NAME, 'folder')
        assert len(folders) == 4

        created = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'created'))

        for element in created:
            WebDriverWait(driver, 30).until(lambda d: 'default' in element.get_attribute('class'))

        loaded_presentations = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'default'))
        assert len(loaded_presentations) == 4

        app_sidebar = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'AppSidebar'))
        sidebar_buttons = app_sidebar.find_elements(By.TAG_NAME, 'button')

        build_presentation_button = sidebar_buttons[1]
        assert build_presentation_button.text == 'Сборка презентации'

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable(build_presentation_button)).click()

        toolbar = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'toolbar'))

        import_slides_button = toolbar.find_element(By.TAG_NAME, 'button')
        assert import_slides_button.text == 'Импорт слайдов'

        import_slides_button.click()

        import_slides = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'import-slides'))
        buttons = import_slides.find_elements(By.TAG_NAME, 'button')

        presentation_filter = WebDriverWait(driver, 30).until(
            lambda d: import_slides.find_element(By.CLASS_NAME, 'presentation-filter'))
        presentation_filter_inputs = presentation_filter.find_elements(By.TAG_NAME, 'input')
        presentation_filter_button = buttons[0]
        assert presentation_filter_button.text == 'Снять выделение'

        import_button = buttons[1]
        assert import_button.text == 'Импорт слайдов'

        presentation_filter_button.click()

        assert not any([inpt.get_attribute('selected') == 'true' for inpt in presentation_filter_inputs])

        presentation_filter_inputs[0].click()
        presentation_filter_inputs[1].click()

        import_button.click()
        time.sleep(0.2)

        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'PoolSlideCard'))
        assert len(slides) == 6

        move_all_button = driver.find_element(By.ID, 'moveAllBtn')
        move_selected_button = driver.find_element(By.ID, 'moveSelectedBtn')

        move_all_button.click()

        preview_slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'PreviewSlideCard'))
        assert len(preview_slides) == 6

        drop_pads = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'DropPad'))
        assert len(drop_pads) == 7

        action_chains.click_and_hold(driver.find_elements(By.CLASS_NAME, 'PreviewSlideCard')[0])
        action_chains.release(driver.find_elements(By.CLASS_NAME, 'DropPad')[2])
        action_chains.pause(2)
        action_chains.perform()

        for _ in preview_slides:
            preview_slide = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'PreviewSlideCard'))
            action_chains.context_click(preview_slide).perform()


        with self.assertRaises(TimeoutException):
            WebDriverWait(driver, 2).until(
                lambda d: d.find_element(By.TAG_NAME, 'PreviewSlideCard'))

        import_slides_button.click()

        import_slides = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'import-slides'))
        buttons = import_slides.find_elements(By.TAG_NAME, 'button')

        presentation_filter = WebDriverWait(driver, 30).until(
            lambda d: import_slides.find_element(By.CLASS_NAME, 'presentation-filter'))
        presentation_filter_inputs = presentation_filter.find_elements(By.TAG_NAME, 'input')
        presentation_filter_button = buttons[0]
        assert presentation_filter_button.text == 'Снять выделение'

        import_button = buttons[1]
        assert import_button.text == 'Импорт слайдов'

        presentation_filter_button.click()

        assert not any([inpt.get_attribute('selected') == 'true' for inpt in presentation_filter_inputs])

        presentation_filter_inputs[2].click()
        presentation_filter_inputs[3].click()

        import_button.click()
        time.sleep(0.2)

        slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'PoolSlideCard'))
        assert len(slides) == 6

        slides[0].click()
        slides[1].click()
        slides[3].click()
        slides[4].click()

        move_selected_button.click()

        preview_slides = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'PreviewSlideCard'))
        assert len(preview_slides) == 4

        preview_slide_block = driver.find_element(By.CLASS_NAME, 'PresentationPreviewBlock')
        build_btn = preview_slide_block.find_element(By.TAG_NAME, 'button')
        assert build_btn.text == 'Собрать презентацию'

        build_btn.click()

        pres_name = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'pres-name'))
        pres_name_input = pres_name.find_element(By.TAG_NAME, 'input')

        save_to = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'save-to'))
        save_to_button = save_to.find_element(By.TAG_NAME, 'button')

        template_cards = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'TemplateCard'))

        ratio_filter = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'ratio-filter'))
        ratio_filter_input = ratio_filter.find_elements(By.TAG_NAME, 'input')

        pres_name_input.send_keys('Новая презентация')

        assert len(template_cards) == 2

        ratio_filter_input[1].click()
        ratio_filter_input[0].click()

        template_cards[0].click()
        template_cards[1].click()
        template_cards[1].click()

        save_to_button.click()

        select_folder = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'select-folder'))
        select_folder_buttons = select_folder.find_elements(By.TAG_NAME, 'button')

        ok_button = select_folder_buttons[0]
        assert ok_button.text == 'Ок'

        back_button = select_folder_buttons[1]
        assert back_button.text == 'Назад'

        folders = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        assert len(folders) == 4
        folder3 = next((folder for folder in folders if folder.text == 'Папка 3'), None)
        folder3.click()

        time.sleep(2)

        folders = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))

        back_button.click()


        folders = WebDriverWait(driver, 30).until(lambda d: d.find_elements(By.CLASS_NAME, 'Folder'))
        assert len(folders) == 4
        build_folder = next((folder for folder in folders if folder.text == 'Собранные презентации'), None)

        build_folder.click()
        ok_button.click()

        build_presentation = driver.find_element(By.CLASS_NAME, 'build-presentation')
        build_presentation_buttons = build_presentation.find_elements(By.TAG_NAME, 'button')
        build_button = next((btn for btn in build_presentation_buttons if btn.text == 'Собрать презентацию'), None)
        assert build_button is not None

        build_button.click()

        build_done_consent = WebDriverWait(driver, 30).until(lambda d: d.find_element(By.CLASS_NAME, 'build-done-consent'))
        build_done_buttons = build_done_consent.find_elements(By.TAG_NAME, 'button')

        download_button = build_done_buttons[0]
        assert download_button.text == 'Скачать'

        download_button.click()


        coverage = driver.execute_script('return JSON.stringify(__coverage__)')
        with open(os.path.join(ROOT, f'client/coverage_raw/test_build_presentation_coverage.json'), 'w') as file:
            file.write(coverage)

        driver.close()

    @classmethod
    def tearDownClass(cls):
        cls.db_handler.clear_db()
        cls.db_handler.pool.close()

if __name__ == '__main__':
    unittest.main()
