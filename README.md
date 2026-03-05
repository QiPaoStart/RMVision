# RMVision
An auto-aiming model for RoboMaster robots, trained on [YOLOv5](https://github.com/ultralytics/yolov5).

一款基于[YOLOv5](https://github.com/ultralytics/yolov5)训练的RoboMaster机器人自动瞄准模型。

Use dataset: <https://universe.roboflow.com/purobocon/test-rm>

模型训练使用数据集: <https://universe.roboflow.com/purobocon/test-rm>

### 文件组成

[best_robo_3.pt](https://github.com/QiPaoStart/RMVision/blob/main/best_robo_3.pt) - YOLOv5权重文件

[yolov5_api.py](https://github.com/QiPaoStart/RMVision/blob/main/yolov5_api.py) - 调用已训练模型的简易API

[yolov5_api_test.py](https://github.com/QiPaoStart/RMVision/blob/main/yolov5_api_test.py), [rule.py](https://github.com/QiPaoStart/RMVision/blob/main/rule.py) - 基于简易API的示例RoboMaster机器人操控程序, 及RoboMaster机器人对战规则程序, 可用于演示

[runs/train/exp10](https://github.com/QiPaoStart/RMVision/tree/main/runs/train/exp10) - 模型训练结果
