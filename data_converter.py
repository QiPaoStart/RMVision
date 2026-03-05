# -*- coding: utf-8 -*-

import json
import os

import cv2

def alpha2white_opencv2(imgo):
    img=imgo.copy()
    sp=img.shape
    width=sp[0]
    height=sp[1]
    for yh in range(height):
        for xw in range(width):
            color_d=img[xw,yh]
            if color_d.size <= 3:
                return img
            if(color_d[3]==0):
                img[xw,yh]=[255,255,255,255]
    return img

# 图片路径文件夹必须包含images关键字
train_root_path = './train/arknights/'
image_path = 'images/'
dict_path = 'dict.json'
output_path = 'outputs/'

available_suffixes = ['.jpg', '.png', '.gif', '.jfif']

fs = os.listdir(train_root_path + output_path)

_dict = json.load(open(train_root_path + dict_path))

print_path = train_root_path + image_path
print_path = print_path.replace('/images', '/labels').replace(r'\\images', r'\\labels').replace(r'\images', r'\labels')
try:
    os.mkdir(print_path)
except FileExistsError:
    pass

for f in fs:
    if f.endswith('.json'):
        print('Processing File: ' + f)
        f = train_root_path + output_path + f
        file = open(f)
        obj = json.load(file)
        img_pth = obj['path']
        img = cv2.imread(img_pth)
        img_new = alpha2white_opencv2(img)
        print('Convert Alpha Done: ' + f)
        cv2.imwrite(img_pth, img_new)
        output_pth = img_pth.replace('/images', '/labels').replace(r'\\images', r'\\labels').replace(r'\images', r'\labels')
        for suffix in available_suffixes:
            output_pth = output_pth.replace(suffix, '.txt')
        output_file = open(output_pth, 'w') # write mode
        write_lines = []
        try:
            sizes = dict(obj['size'])
            img_x = int(sizes['width'])
            img_y = int(sizes['height'])
            sels = list(dict(obj['outputs'])['object'])
        except KeyError:
            print('Cannot found bound box in file ' + f + ', ignoring...')
            continue
        for target in sels:
            target = dict(target)
            name = str(target['name'])
            try:
                _id = _dict[name]
            except KeyError:
                _id = -1
            bndbox = dict(target['bndbox'])
            xmin = bndbox['xmin']
            xmax = bndbox['xmax']
            ymin = bndbox['ymin']
            ymax = bndbox['ymax']
            x_centre = ((xmin + xmax) / 2) / img_x
            y_centre = ((ymin + ymax) / 2) / img_y
            width = (xmax - xmin) / img_x
            height = (ymax - ymin) / img_y
            x_centre = round(x_centre, 6)
            y_centre = round(y_centre, 6)
            width = round(width, 6)
            height = round(height, 6)
            o = str(_id) + ' ' + str(x_centre) + ' ' + str(y_centre) + ' ' + str(width) + ' ' + str(height)
            write_lines.append(o)
        output_file.writelines(write_lines)
        output_file.close()
        print('Processing Done: ' + f)
    else:
        print('Ignoring File: ' + f)
print('Complete.')
            