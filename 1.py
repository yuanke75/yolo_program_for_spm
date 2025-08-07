import optuna
import optuna.visualization as vis
import subprocess
from copy import deepcopy
import yaml
import os
import pandas as pd
from pathlib import Path
import time

def get_latest_exp_folder(base_path):
    """
    获取最新的exp文件夹路径
    """
    exp_folders = list(Path(base_path).glob('exp*'))
    latest_exp_folder = max(exp_folders, key=os.path.getmtime)  # 根据修改时间找到最新的文件夹
    return latest_exp_folder

def get_next_list_folder(temp_hyp_dir):
    """
    在指定的基础路径下获取下一个list文件夹的名称。
    """
    list_folders = [p for p in Path(temp_hyp_dir).iterdir() if p.is_dir() and p.name.startswith('list')]
    if not list_folders:
        return os.path.join(temp_hyp_dir, 'list1')
    else:
        latest_list_folder = max(list_folders, key=lambda x: int(x.name.replace('list', '')))
        next_list_number = int(latest_list_folder.name.replace('list', '')) + 1
        return os.path.join(temp_hyp_dir, f'list{next_list_number}')
def calculate_f1(f1_path):
    # 初始化一个空列表来存储f1分数
    f1_scores = []

    # 使用with语句打开文件，确保文件正确关闭
    with open(f1_path, 'r') as file:
        # 逐行读取文件
        for line in file:
            # 尝试将每行转换为浮点数并添加到列表中
            try:
                score = float(line.strip())  # 去除可能的空白字符并转换
                f1_scores.append(score)
            except ValueError:
                # 如果转换失败，可以选择打印错误消息或者忽略该行
                print(f"Warning: Unable to convert '{line.strip()}' to float. Skipping.")

    # 根据需要处理f1_scores，例如返回或打印
    return f1_scores


base_path = 'D:/code/yolov9-main/runs/val'
latest_exp_folder = get_latest_exp_folder(base_path)
f1_path = os.path.join(latest_exp_folder, 'f1_scores.txt')
# f1_path = 'runs/val/exp12/f1_scores.txt'
f1 = calculate_f1(f1_path)
f1_min =min(f1)
print(f1_min)