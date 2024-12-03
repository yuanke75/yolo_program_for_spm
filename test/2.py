#我现在的数据集是txt文件，每行代表一个物体，每行有5个数字，第一个是类别，后四个是左上和右下的xy坐标，我现在想把左上和右下的坐标转换成中心点的坐标和长宽  


import os
import glob

def convert_bbox_format(line):
    # 分解每行的数据：类别，左上角x，左上角y，右下角x，右下角y
    category, x1, y1, x2, y2 = map(float, line.split())
    # 计算中心点坐标和宽度高度
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    width = x2 - x1
    height = y2 - y1
    # 返回转换后的字符串
    return f"{int(category)} {cx} {cy} {width} {height}\n"

def process_file(file_path):
    # 读取原始文件内容
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # 转换每一行
    converted_lines = [convert_bbox_format(line) for line in lines]
    # 覆盖原文件
    with open(file_path, 'w') as file:
        file.writelines(converted_lines)

def find_and_convert_txt_files(directory):
    # 遍历目录及其所有子目录
    for root, dirs, files in os.walk(directory):
        # 对于每个目录，找到所有的txt文件
        for file_path in glob.glob(os.path.join(root, '*.txt')):
            # 处理每个找到的txt文件
            process_file(file_path)

# 调用函数，替换以下路径为你的实际目录路径
find_and_convert_txt_files('dataset/voc')

