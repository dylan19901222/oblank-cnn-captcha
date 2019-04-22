
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from keras.models import Sequential
from keras.models import load_model
from keras.models import Model
from keras.layers import Input, Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.layers.normalization import BatchNormalization
from keras.utils  import np_utils
from keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
import csv

dic32 = {'2':0, '3':1, '4':2, '5':3, '6':4,'7':5, '8':6 ,'9':7,'A':8,'B':9,'C':10,
         'D':11,'E':12, 'F':13,'G':14,'H':15,'J':16, 'K':17,'L':18, 'M':19, 'N':20,
         'P':21, 'Q':22, 'R':23, 'S':24,'T':25,'U':26,'V':27,'W':28, 'X':29,'Y':30, 'Z':31}


def to_onelist(text):
    print(text)
    label_list = []
    for c in text:
        onehot = [0 for _ in range(32)]
        print(c)
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



#creat CNN model
print('Creating CNN model...')
tensor_in = Input((60, 152, 3))
tensor_out = tensor_in
tensor_out = Conv2D(filters=32, kernel_size=(3, 3), padding='same', activation='relu')(tensor_out)
tensor_out = Conv2D(filters=32, kernel_size=(3, 3), activation='relu')(tensor_out)
tensor_out = MaxPooling2D(pool_size=(2, 2))(tensor_out)
tensor_out = Conv2D(filters=64, kernel_size=(3, 3), padding='same', activation='relu')(tensor_out)
tensor_out = Conv2D(filters=64, kernel_size=(3, 3), activation='relu')(tensor_out)
tensor_out = MaxPooling2D(pool_size=(2, 2))(tensor_out)
tensor_out = Conv2D(filters=128, kernel_size=(3, 3), padding='same', activation='relu')(tensor_out)
tensor_out = Conv2D(filters=128, kernel_size=(3, 3), activation='relu')(tensor_out)
tensor_out = BatchNormalization(axis=1)(tensor_out)
tensor_out = MaxPooling2D(pool_size=(2, 2))(tensor_out)
tensor_out = Conv2D(filters=256, kernel_size=(3, 3), padding='same', activation='relu')(tensor_out)
tensor_out = Conv2D(filters=256, kernel_size=(3, 3), padding='same', activation='relu')(tensor_out)
tensor_out = MaxPooling2D(pool_size=(2, 2))(tensor_out)
tensor_out = Conv2D(filters=512, kernel_size=(3, 3), padding='same', activation='relu')(tensor_out)
tensor_out = BatchNormalization(axis=1)(tensor_out)
tensor_out = MaxPooling2D(pool_size=(2, 2))(tensor_out)

tensor_out = Flatten()(tensor_out)
tensor_out = Dropout(0.5)(tensor_out)

tensor_out = [Dense(32, name='digit1', activation='softmax')(tensor_out),\
              Dense(32, name='digit2', activation='softmax')(tensor_out),\
              Dense(32, name='digit3', activation='softmax')(tensor_out),\
              Dense(32, name='digit4', activation='softmax')(tensor_out)]

model = Model(inputs=tensor_in, outputs=tensor_out)
model.compile(loss='categorical_crossentropy', optimizer='Adamax', metrics=['accuracy'])
model.summary()
              
print("reading training data...")
train_data = np.stack([np.array(Image.open("../image_denoising/img/" + str(index) + ".jpg"))/255.0 for index in range(1, 5001, 1)])
# train_data = np.stack([np.array(Image.open("../img process plus/img f/" + str(index) + ".jpg"))/255.0 for index in range(1, 4001, 1)])

traincsv = open('label.csv', 'r', encoding = 'utf8')
read_label =  [to_onelist(row[0]) for row in csv.reader(traincsv)]
train_label = [[] for _ in range(4)]
for arr in read_label[:]:
    for index in range(4):
        train_label[index].append(arr[index])
train_label = [arr for arr in np.asarray(train_label)]
print("shape of train data:", train_data.shape)

print("reading validation data...")
vali_data = np.stack([np.array(Image.open("../image_denoising/img/" + str(index) + ".jpg"))/255.0 for index in range(4001, 5001, 1)])
# vali_data = np.stack([np.array(Image.open("../img process plus/img f/"+ str(index) + ".jpg"))/255.0 for index in range(4001, 5000, 1)])

valicsv = open('label.csv', 'r', encoding = 'utf8')
read_label = [to_onelist(row[0]) for row in csv.reader(valicsv)]
vali_label = [[] for _ in range(4)]
for arr in read_label[4000:5000]:
    for index in range(4):
        vali_label[index].append(arr[index])
vali_label = [arr for arr in np.asarray(vali_label)]
print("shape of train data:", vali_data.shape)


filepath='../predicting/oblank_cnn_model.hdf5'
try:
    model = load_model(filepath)
    print('model is loaded...')
except:
    model.save(filepath)
    print('training new model...')

checkpoint = ModelCheckpoint(filepath, monitor='val_digit4_acc', verbose=1, save_best_only=True, mode='max')
earlystop = EarlyStopping(monitor='val_loss', patience=8, verbose=1, mode='auto')
tensorBoard = TensorBoard(log_dir = 'logs', histogram_freq = 1)
callbacks_list = [tensorBoard, earlystop, checkpoint]
model.fit(train_data, train_label, batch_size=50, epochs=40, verbose=2, validation_data=(vali_data, vali_label), callbacks=callbacks_list)
#.fit(train_data, train_label, validation_split=0.2, batch_size=50, epochs=20, verbose=2, callbacks=callbacks_list)
# tensorboard --logdir= (dist)