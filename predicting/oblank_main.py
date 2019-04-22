from PIL import Image, ImageDraw, ImageFont
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium import webdriver
from seleniumrequests import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from keras.models import Sequential
from keras.models import load_model
from keras.models import Model
from keras.layers import Input, Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.utils  import np_utils
from keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
import numpy as np
import time
import base64
import configparser
import os

mConfigParser = configparser.RawConfigParser()
mConfigParser.read(os.path.abspath('.') + '/config.ini')
no = mConfigParser.get('USER','no')
uno = mConfigParser.get('USER','uno')
sec = mConfigParser.get('USER','sec')

oblank_url = mConfigParser.get('WEB','oblank_url')
executable_path = mConfigParser.get('WEBDRIVER','path')


dic32 = {'2':0, '3':1, '4':2, '5':3, '6':4,'7':5, '8':6 ,'9':7,'A':8,'B':9,'C':10,
         'D':11,'E':12, 'F':13,'G':14,'H':15,'J':16, 'K':17,'L':18, 'M':19, 'N':20,
         'P':21, 'Q':22, 'R':23, 'S':24,'T':25,'U':26,'V':27,'W':28, 'X':29,'Y':30, 'Z':31}

def to_text2(int):
    text = []
    text.append(list(dic32.keys())[list(dic32.values()).index(int)])
    return "".join(text)

# 去噪、黑白化圖片
def convert_img(source_path , target_path):
    img=Image.open(source_path)
    pixdata = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if((pixdata[x, y][0] > 0 ) and (pixdata[x, y][0] < 100)  \
            and (pixdata[x, y][2] > 80 ) and (pixdata[x, y][2] < 240)) \
            or ((pixdata[x, y][0] > 100 ) and (pixdata[x, y][0] < 130)
            and (pixdata[x, y][1] > 210 ) and (pixdata[x, y][1] < 230)  \
            and (pixdata[x, y][2] > 200 ) and (pixdata[x, y][2] < 255)) :

                pixdata[x, y] = (255, 255, 255, 255)
            else:
                pixdata[x, y] = (0, 0, 0, 255) 
    img.save(target_path,"JPEG")


def login(no, uno , sec):

    browser = Chrome(executable_path = executable_path)
    
    browser.get(oblank_url)

    # 確認是在王道銀行頁面中, 以防被轉向做其他的事情
    assert "王道銀行" in browser.title

    
    delay = 10 # seconds
    try:
        myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'no')))
        # 輸入使用者身分證
        elem = browser.find_element_by_id("no") 
        elem.send_keys(no)
        # 輸入使用者代號
        elem = browser.find_element_by_id("uno")
        elem.send_keys(uno)
        # 輸入使用者密碼
        elem = browser.find_element_by_id("sec")
        elem.send_keys(sec)
        
        print('model loading...')
        model = load_model('oblank_cnn_model.hdf5')

        elem = browser.find_element_by_id("captchaImage")
        elem = elem.find_element_by_tag_name('img')
        src = elem.get_attribute("src")
        # decode
        tmp_jpg = base64.b64decode(src[23:])
        file_path = "temp.jpg"
        # save to a file
        with open(file_path, 'wb') as f:
            f.write(tmp_jpg)

        print("Convert Image...")
        convert_img(file_path,file_path)
        
        print("Reading data...")
        x_train = np.stack([np.array(Image.open(file_path))/255.0])
        
        
        print('predict start')
        prediction = model.predict(x_train)

        predict_text=""
        for predict in prediction:
            predict_text+=to_text2(np.argmax(predict))
            
        print(predict_text)
        elem = browser.find_element_by_id("captcha")
        elem.send_keys(predict_text)
        
        nextElements = browser.find_elements_by_xpath("//*[@class='submit_btn mb10 bindonce bindevent']")
        ActionClick = ActionChains(browser).click(nextElements[0])
        ActionClick.perform() 
        time.sleep(10)
        #我的帳戶
        elem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'B')))
        # elem = browser.find_element_by_id("B")
        ActionClick = ActionChains(browser).click(elem)
        ActionClick.perform()
        time.sleep(5)

        #買賣外匯
        elem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'B09')))
        ActionClick = ActionChains(browser).click(elem)
        ActionClick.perform()
        
        time.sleep(5)
        myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH,"//*[@class='card_btn mb10 bindonce bindevent']")))
        nextElements = browser.find_elements_by_xpath("//*[@class='card_btn mb10 bindonce bindevent']")
        ActionClick = ActionChains(browser).click(nextElements[0])
        ActionClick.perform()
        


        #logout
        time.sleep(15)
        elem = browser.find_element_by_id("logout_btn")
        ActionClick = ActionChains(browser).click(elem)
        ActionClick.perform()
        elem = browser.find_element_by_id("confirmModalBtn1")
        ActionClick = ActionChains(browser).click(elem)
        ActionClick.perform() 
        print("already logout") 
        # captchaWarning
    except TimeoutException:
        elem = browser.find_element_by_id("logout_btn")
        ActionClick = ActionChains(browser).click(elem)
        ActionClick.perform()
        elem = browser.find_element_by_id("confirmModalBtn1")
        ActionClick = ActionChains(browser).click(elem)
        ActionClick.perform() 
        print("already logout")
        print("loading took too much time!")
    
    return browser






if __name__ == '__main__':
    login(no,uno,sec)