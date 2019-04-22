from PIL import Image, ImageDraw, ImageFont
import numpy as np
from keras.models import Sequential
from keras.models import load_model
from keras.models import Model
from keras.layers import Input, Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.utils  import np_utils
from keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
import csv
import time


dic32 = {'2':0, '3':1, '4':2, '5':3, '6':4,'7':5, '8':6 ,'9':7,'A':8,'B':9,'C':10,
         'D':11,'E':12, 'F':13,'G':14,'H':15,'J':16, 'K':17,'L':18, 'M':19, 'N':20,
         'P':21, 'Q':22, 'R':23, 'S':24,'T':25,'U':26,'V':27,'W':28, 'X':29,'Y':30, 'Z':31}

def to_onelist(text):
    label_list = []
    for c in text:
        onehot = [0 for _ in range(32)]
        onehot[ dic32[c] ] = 1
        label_list.append(onehot)
    return label_list

def to_text(l_list):
    text=[]
    pos = []
    for i in range(4):
        for j in range(32):
            if(l_list[i][j]):
                pos.append(j)

    for i in range(4):
        char_idx = pos[i]
        text.append(list(dic32.keys())[list(dic32.values()).index(char_idx)])
        return "".join(text)

def to_text2(int):
    text = []
    text.append(list(dic32.keys())[list(dic32.values()).index(int)])
    return "".join(text)

def test_model():
    print('model loading...')
    model = load_model('oblank_cnn_model.hdf5')
    start = 5001
    test_num = 20 #test number

    print("Reading data...")
    # x_train = np.stack([np.array(Image.open("/Users/dylan-zheng/Desktop/OCR/data/" + str(index) + ".jpg"))/255.0 for index in range(1, test_num, 1)])
    x_train = np.stack([np.array(Image.open("../image_denoising/img/" + str(index) + ".jpg"))/255.0 for index in range(start, start + test_num, 1)])

    print('predict start')

    prediction = model.predict(x_train)
    print('preficted ')
    resultlist = ["" for _ in range(test_num-1)]

    for predict in prediction:
        for index in range(test_num-1):
            resultlist[index] += to_text2(np.argmax(predict[index]))


    for result in resultlist:
        print(result)


if __name__ == '__main__':
    test_model()


