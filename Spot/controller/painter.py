import base64
from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


options = webdriver.ChromeOptions()
options.headless = True

def paint_picture(html_string: str) -> str:
    html_bs64 = base64.b64encode(html_string.encode('utf-8')).decode()
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.set_window_size(1500,900)
    driver.get("data:text/html;base64, " + html_bs64)
    sleep(1)
    photo_string = driver.get_screenshot_as_png()
    driver.quit()
    return photo_string
