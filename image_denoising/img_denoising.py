import cv2
from PIL import Image

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

num = 1
count = 50 
target_path = ""
while (num <= count):
    print(num)
    if num < count/2 + 1 :
        target_path = "./img/"+str(num)+".jpg"
    else :
        target_path = "./test_img/"+str(num)+".jpg"

    convert_img("../image_crawler/img/"+str(num)+".jpg" , target_path)
    num+=1
