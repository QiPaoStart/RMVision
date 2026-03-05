# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 10:52:50 2023

@author: wangjiayu
"""

import os
import sys
from pathlib import Path
import numpy as np
import cv2
import torch
import torch.backends.cudnn as cudnn
from models.common import DetectMultiBackend
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_segments, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync
from utils.augmentations import Albumentations, augment_hsv, copy_paste, letterbox, mixup, random_perspective

#改编自YOLOv5 - detect.py
class yolov5_api:
    
    weights = "best_robo_3.pt"
    data = "robo.yaml"
    device_name = "cpu"
    device = select_device("cpu")

    imgsz=(640, 640)
    conf_thres=0.25
    iou_thres=0.45
    max_det=1000
    device='0'
    classes=None
    agnostic_nms=False
    augment=False
    visualize=False
    half=False
    dnn=False
    logger=False
    line_thickness=3

    def __init__(self, weights="best_robo_3.pt", data="robo.yaml", device="cpu"):
        FILE = Path(__file__).resolve()
        ROOT = FILE.parents[0]
        if str(ROOT) not in sys.path:
            sys.path.append(str(ROOT))
        ROOT = Path(os.path.relpath(ROOT, Path.cwd()))
        self.weights = weights
        self.data = data
        self.device_name = device
        print("------INIT COMPLETE------")

    def load(self):
        self.device = select_device(self.device_name)
        self.model = DetectMultiBackend(self.weights, device=self.device, dnn=self.dnn, data=self.data)
        self.stride, self.names, self.pt, self.jit, self.onnx, self.engine = self.model.stride, self.model.names, self.model.pt, self.model.jit, self.model.onnx, self.model.engine
        self.imgsz = check_img_size(self.imgsz, s=self.stride)
    
        self.half &= (self.pt or self.jit or self.onnx or self.engine) and self.device.type != 'cpu'  # FP16 supported on limited backends with CUDA
        if self.pt or self.jit:
            self.model.model.half() if self.half else self.model.model.float()
    
    def __detect(self, img):
        
        self.model.warmup(imgsz=(1, 3, *self.imgsz))
        dt, seen = [0.0, 0.0, 0.0], 0

        im0 = img

        im = letterbox(im0, self.imgsz, self.stride, auto=self.pt)[0]

        im = im.transpose((2, 0, 1))[::-1]
        im = np.ascontiguousarray(im)
        t1 = time_sync()
        im = torch.from_numpy(im).to(self.device)
        im = im.half() if self.half else im.float()
        im /= 255
        if len(im.shape) == 3:
            im = im[None]
        t2 = time_sync()
        dt[0] += t2 - t1

        pred = self.model(im, augment=self.augment, visualize=self.visualize)
        t3 = time_sync()
        dt[1] += t3 - t2

        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, self.classes, self.agnostic_nms, max_det=self.max_det)
        dt[2] += time_sync() - t3

        detections=[]

        for i, det in enumerate(pred):
            seen += 1
            imc = im0.copy()
            annotator = Annotator(imc, line_width=self.line_thickness, example=str(self.names))
            if len(det):
                
                det[:, :4] = scale_segments(im.shape[2:], det[:, :4], im0.shape).round()
                
                for *xyxy, conf, cls in reversed(det):
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4))).view(-1).tolist()
                    xywh = [round(x) for x in xywh]
                    xywh = [xywh[0] - xywh[2] // 2, xywh[1] - xywh[3] // 2, xywh[2],
                            xywh[3]]
                    c = int(cls)
                    cls = self.names[int(cls)]
                    conf = float(conf)
                    annotator.box_label(xyxy, cls, color=colors(c, True))
                    detections.append({'class': cls, 'conf': conf, 'position': xywh})
            imc = annotator.result()

        if self.logger: 
            LOGGER.info(f'({t3 - t2:.3f}s)')
        return detections, imc

    def detect(self, img):
        res, ignored = self.__detect(img)
        return res

    def detect_with_image(self, img):
        return self.__detect(img)

    def convert_box(self, res):
        robo = []
        red = []
        blue = []

        for i in res:
            dic = dict(i)
            if dic['class'] == 'RoboMaster':
                robo.append(dic['position'])
            if dic['class'] == 'OvalArmorBlue':
                blue.append(dic['position'])
            if dic['class'] == 'OvalArmorRed':
                red.append(dic['position'])
        return robo, red, blue

    def get_box_center(self, box):
        l = list(box)
        x = l[0] + (l[2] / 2)
        y = l[1] + (l[3] / 2)
        return (x, y)

    def convert_center(self, res):

        robo = []
        red = []
        blue = []

        for i in res:
            dic = dict(i)
            if dic['class'] == 'RoboMaster':
                robo.append(self.get_box_center(dic['position']))
            if dic['class'] == 'OvalArmorBlue':
                blue.append(self.get_box_center(dic['position']))
            if dic['class'] == 'OvalArmorRed':
                red.append(self.get_box_center(dic['position']))

        return robo, red, blue
