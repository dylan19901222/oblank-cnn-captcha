from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium import webdriver
from seleniumrequests import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import base64
import configparser
import os


mConfigParser = configparser.RawConfigParser()
mConfigParser.read(os.path.abspath('.') + '/config.ini')
oblank_url = mConfigParser.get('WEB','oblank_url')
executable_path = mConfigParser.get('WEBDRIVER','path')

use_headless = True

def crawler_captcha_image():

    #使用headless
    chromeOptions = webdriver.ChromeOptions()
    if use_headless :
        chromeOptions.add_argument('--headless')
        chromeOptions.add_argument('--log-level=3')
    #指定web driver 位置
    browser = webdriver.Chrome(executable_path = executable_path,chrome_options = chromeOptions)
    #欲抓取網站
    browser.get(oblank_url)

    #確認是在王道銀行頁面中
    assert "王道銀行" in browser.title

    #延遲秒數，單位seconds
    delay = 10
    count = 10000
    SAVEPATH = "./new_img/"
    try:
        myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'no')))  
        num=1
        while (num <= count):
            print(num)
            elem = browser.find_element_by_id("captchaImage")
            elem = elem.find_element_by_tag_name('img')
            src = elem.get_attribute("src")
            # decode
            tmp_jpg = base64.b64decode(src[23:])
            
            # save to a file
            with open(SAVEPATH+str(num)+'.jpg', 'wb') as f:
                f.write(tmp_jpg)
            num+=1
            
            nextElements = browser.find_elements_by_xpath("//*[@class='btn_refresh bindonce bindevent']")
            ActionClick = ActionChains(browser).click(nextElements[0])
            ActionClick.perform() 
            time.sleep(3)

        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")
    

    return browser

if __name__ == '__main__':
    crawler_captcha_image()