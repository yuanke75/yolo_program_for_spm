import optuna
from optuna.pruners import MedianPruner
import subprocess
from copy import deepcopy
import yaml
import os
import pandas as pd
from pathlib import Path
import time
import traceback
import matplotlib.pyplot as plt
import optuna.visualization as vis
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




# def save_visualizations(study):
#     if len(study.trials) == 0:
#         print("没有试验数据可用于生成可视化。")
#         return

#     # 检查并创建可视化保存目录
#     vis_dir = 'vis'
#     os.makedirs(vis_dir, exist_ok=True)

#     try:
#         plt.figure(figsize=(10, 8))
#         fig = vis.plot_optimization_history(study)
#         fig.write_image(os.path.join(vis_dir, 'optimization_history.png'))
#         plt.close()

#         plt.figure(figsize=(10, 8))
#         fig = vis.plot_parallel_coordinate(study)
#         fig.write_image(os.path.join(vis_dir, 'parallel_coordinate.png'))
#         plt.close()

#         plt.figure(figsize=(10, 8))
#         fig = vis.plot_contour(study)
#         fig.write_image(os.path.join(vis_dir, 'contour.png'))
#         plt.close()

#         plt.figure(figsize=(10, 8))
#         fig = vis.plot_slice(study)
#         fig.write_image(os.path.join(vis_dir, 'slice.png'))
#         plt.close()

#         plt.figure(figsize=(10, 8))
#         fig = vis.plot_param_importances(study)
#         fig.write_image(os.path.join(vis_dir, 'param_importances.png'))
#         plt.close()
#     except Exception as e:
#         print(f"生成或保存可视化时发生错误: {e}")

def extract_map_from_results_csv(csv_path):
    """
    从results.csv文件中提取mAP@0.5和mAP@0.5:0.95。
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Expected results.csv not found at {csv_path}")
    print(f"尝试读取文件: {csv_path}")  # 打印文件路径
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Expected results.csv not found at {csv_path}")
    df = pd.read_csv(csv_path)
    print("文件列名:", df.columns)  # 打印DataFrame的列名
    try:
        last_row = df.iloc[-1]
        map50 = last_row['     metrics/mAP_0.5']
        map95 = last_row['metrics/mAP_0.5:0.95']
        return map50, map95
    except KeyError as e:
        print(f"在DataFrame中找不到列: {e}")
        raise
def print_best_trial(study, trial):
    # Optuna在每次试验后调用此函数
    print(f"\n当前最佳试验: {study.best_trial.number}")
    print(f"当前最佳值: {study.best_trial.value}")
    print(f"当前最佳参数: {study.best_trial.params}\n")
    
def parse_output(output):
    """
    从输出中解析出 mAP@0.5 和 mAP@0.5-0.95 的值。
    假设输出格式如上图，mAP50 和 mAP50-95 的值在对应标签的下一行。
    """
    lines = output.split('\n')
    # 初始化结果列表
    results = []

    # 找出包含 'mAP50' 和 'mAP50-95:' 的列索引
    for i, line in enumerate(lines):
        if 'mAP50' in line:
            # 获取列索引
            mAP50_idx = line.split().index('mAP50')
            mAP95_idx = line.split().index('mAP50-95:')

            # 确保下一行存在，并且在此列有值
            if i+1 < len(lines):
                next_line = lines[i+1].split()
                map50 = float(next_line[mAP50_idx]) if mAP50_idx < len(next_line) else None
                map95 = float(next_line[mAP95_idx]) if mAP95_idx < len(next_line) else None
                results.append((map50, map95))

    return results

def objective(trial, next_list_dir):
    # temp_hyp_dir = 'temp_hyp'
    # os.makedirs(temp_hyp_dir, exist_ok=True)
    # # 获取下一个list文件夹路径并创建
    # next_list_dir = get_next_list_folder(temp_hyp_dir)
    # os.makedirs(next_list_dir, exist_ok=True)

    # 为每个超参数定义搜索空间
    # optimizer_choice = trial.suggest_categorical('optimizer', ['SGD', 'Adam'])
    optimizer_choice = trial.suggest_categorical('optimizer', ['SGD'])
    # lr0 = trial.suggest_loguniform('lr0_sgd', 1e-4, 1e-1) if optimizer_choice == 'SGD' else trial.suggest_loguniform('lr0_adam', 1e-5, 1e-2)
    lr0 = trial.suggest_loguniform('lr0', 1e-5, 1e-1) 
    momentum = trial.suggest_uniform('momentum_sgd', 0.85, 0.99) if optimizer_choice == 'SGD' else trial.suggest_uniform('momentum_adam', 0.85, 0.99)
    lrf = trial.suggest_uniform('lrf', 0.01, 1.0)
    weight_decay = trial.suggest_loguniform('weight_decay', 1e-10, 0.01)
    warmup_epochs = trial.suggest_uniform('warmup_epochs', 0, 5)
    warmup_momentum = trial.suggest_uniform('warmup_momentum', 0.5, 0.95)
    warmup_bias_lr = trial.suggest_uniform('warmup_bias_lr', 0.01, 0.1)
    box = trial.suggest_uniform('box', 0.5, 10.0)
    cls = trial.suggest_uniform('cls', 0.5, 1.0)
    cls_pw = trial.suggest_uniform('cls_pw', 0.5, 2.0)
    obj = trial.suggest_uniform('obj', 0.5, 1.0)
    obj_pw = trial.suggest_uniform('obj_pw', 0.5, 2.0)
    dfl = trial.suggest_uniform('dfl', 0.5, 2.0)
    iou_t = trial.suggest_uniform('iou_t', 0.1, 0.7)
    anchor_t = trial.suggest_uniform('anchor_t', 2.0, 10.0)
    fl_gamma = trial.suggest_uniform('fl_gamma', 0, 5.0)
    mosaic = trial.suggest_uniform('mosaic', 0.5, 1)
    hsv_h= trial.suggest_uniform('hsv_h', 0  , 0.015  ) 
    hsv_s= trial.suggest_uniform('hsv_s', 0 , 0.7 ) 
    hsv_v= trial.suggest_uniform('hsv_v', 0 , 0.4 ) 
    degrees= trial.suggest_uniform('degrees', 0.0, 0.5)
    translate= trial.suggest_uniform('translate', 0.1, 0.5) 
    scale= trial.suggest_uniform('scale',0.7, 0.9) 
    shear= trial.suggest_uniform('shear', 0.0, 0.3) 
    perspective= trial.suggest_uniform('perspective', 0.0, 0.0)
    flipud= trial.suggest_uniform('flipud', 0.0 , 0.5 ) 
    fliplr= trial.suggest_uniform('fliplr', 0,0.5) 
    mixup= trial.suggest_uniform('mixup', 0.15, 0.3) 
    copy_paste= trial.suggest_uniform('copy_paste', 0, 0.3) 
    # 打印当前试验的超参数
    print(f"\nTrial parameters:\n"
        f"Optimizer: {optimizer_choice}, "
        f"lr0: {lr0}, "
        f"Momentum: {momentum}, "
        f"Learning rate factor (lrf): {lrf}, "
        f"Weight decay: {weight_decay}, "
        f"Warmup epochs: {warmup_epochs}, "
        f"Warmup momentum: {warmup_momentum}, "
        f"Warmup bias lr: {warmup_bias_lr}, "
        f"Box: {box}, "
        f"Class: {cls}, "
        f"Class power (cls_pw): {cls_pw}, "
        f"Object: {obj}, "
        f"Object power (obj_pw): {obj_pw}, "
        f"DFL: {dfl}, "
        f"IoU threshold (iou_t): {iou_t}, "
        f"Anchor threshold (anchor_t): {anchor_t}, "
        f"Focal loss gamma (fl_gamma): {fl_gamma}, "
        f"Mosaic: {mosaic}, "
        f"HSV Hue (hsv_h): {hsv_h}, "
        f"HSV Saturation (hsv_s): {hsv_s}, "
        f"HSV Value (hsv_v): {hsv_v}, "
        f"Degrees: {degrees}, "
        f"Translate: {translate}, "
        f"Scale: {scale}, "
        f"Shear: {shear}, "
        f"Perspective: {perspective}, "
        f"Flip UD (flipud): {flipud}, "
        f"Flip LR (fliplr): {fliplr}, "
        f"Mixup: {mixup}, "
        f"Copy Paste: {copy_paste}")


    # 创建临时超参数YAML文件
    hyp = deepcopy(locals())
    del hyp['trial']
    hyp_file = os.path.join(next_list_dir, f'hyp_trial_{trial.number}.yaml')
    with open(hyp_file, 'w') as f:
        yaml.dump(hyp, f, sort_keys=False)
    

    # 调用train.py进行训练
    command = f'python train.py --hyp {hyp_file}'
    subprocess.run(command, shell=True)




    # 查找最新的exp文件夹
    base_path = 'D:/code/yolov9-main/runs/train'
    latest_exp_folder = get_latest_exp_folder(base_path)
    results_csv_path = os.path.join(latest_exp_folder, 'results.csv')
    while not os.path.exists(results_csv_path):
        print("等待 results.csv...")
        time.sleep(10)  # 每10秒检查一次
    map50, map95 = extract_map_from_results_csv(results_csv_path)

    print(f"Trial result: mAP@0.5: {map50}, mAP@0.5:0.95: {map95}")

    return map95


def main():
    temp_hyp_dir = 'temp_hyp'
    os.makedirs(temp_hyp_dir, exist_ok=True)
    next_list_dir = get_next_list_folder(temp_hyp_dir)
    os.makedirs(next_list_dir, exist_ok=True)
    study = optuna.create_study(direction='maximize',storage='sqlite:///db.sqlite3')
    study.optimize(lambda trial: objective(trial, next_list_dir), n_trials=30)
    # save_visualizations(study)
if __name__ == '__main__':
    main()
