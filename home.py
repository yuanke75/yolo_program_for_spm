import os
HOME = os.getcwd()
print(HOME)


# D:/桌面/yolov9-main/data
# !wget -P D:/桌面/yolov9-main/data -q https://media.roboflow.com/notebooks/examples/dog.jpeg

# python detect.py --weights D:/桌面/yolov9-main/weights/yolov9-e.pt --conf 0.1 --source D:/桌面/yolov9-main/data/dog.jpeg --
# python detect.py --weights D:/桌面/yolov9-main/weights/gelan-c.pt --conf 0.1 --source D:/桌面/yolov9-main/data/dog.jpeg --device 0 
# python detect.py --weights D:/桌面/yolov9-main/weights/yolov9-e.pt --conf 0.1 --source D:/桌面/yolov9-main/data/dog.jpeg --device 0 