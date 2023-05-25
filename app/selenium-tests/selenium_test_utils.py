import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def do_login(driver):
    app_header = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, 'AppHeader'))

    app_header_button_block = app_header.find_element(By.CLASS_NAME, 'button-block')

    buttons = app_header_button_block.find_elements(By.TAG_NAME, 'button')
    assert len(buttons) == 3

    user_button = buttons[2]
    assert user_button.accessible_name == 'Users'

    WebDriverWait(driver, timeout=30)\
        .until(expected_conditions.element_to_be_clickable(user_button))\
        .click()

    WebDriverWait(driver, timeout=30)\
        .until(lambda d: d.find_element(By.CLASS_NAME, 'loginBtn'))\
        .click()

    email_input = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.NAME, 'identifier'))
    WebDriverWait(driver, timeout=30)\
        .until(expected_conditions.element_to_be_clickable(email_input))\
        .send_keys('presentation.configurator@gmail.com')

    next_btn = driver.find_element(By.ID, 'identifierNext')
    next_btn.click()

    password_input = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.NAME, 'Passwd'))
    WebDriverWait(driver, timeout=30)\
        .until(expected_conditions.element_to_be_clickable(password_input))\
        .send_keys('polytech2019.')

    next_btn = driver.find_element(By.ID, 'passwordNext')
    next_btn.click()

def do_logout(driver):
    app_header = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, 'AppHeader'))

    app_header_button_block = app_header.find_element(By.CLASS_NAME, 'button-block')

    buttons = app_header_button_block.find_elements(By.TAG_NAME, 'button')
    assert len(buttons) == 3

    user_button = buttons[2]
    assert user_button.accessible_name == 'Users'

    WebDriverWait(driver, timeout=30) \
        .until(expected_conditions.element_to_be_clickable(user_button)) \
        .click()

    app_header.click()

    WebDriverWait(driver, timeout=30) \
        .until(expected_conditions.element_to_be_clickable(user_button)) \
        .click()

    WebDriverWait(driver, timeout=30) \
        .until(lambda d: d.find_element(By.CLASS_NAME, 'logoutBtn')) \
        .click()

def dummy_send(element, word, delay):
    for c in word:
        element.send_keys(c)
        time.sleep(delay)

