import optuna
import optuna.visualization as vis
import subprocess
from copy import deepcopy
import yaml
import os
import pandas as pd
from pathlib import Path
import time
import traceback
import optuna
import traceback
import plotly


def get_latest_exp_folder(base_path):
    """
    获取最新的exp文件夹路径
    """
    exp_folders = list(Path(base_path).glob('exp*'))
    latest_exp_folder = max(exp_folders, key=os.path.getmtime)  # 根据修改时间找到最新的文件夹
    return latest_exp_folder

# def get_next_list_folder(temp_hyp_dir):
#     """
#     在指定的基础路径下获取下一个list文件夹的名称。
#     """
#     list_folders = [p for p in Path(temp_hyp_dir).iterdir() if p.is_dir() and p.name.startswith('list')]
#     if not list_folders:
#         return os.path.join(temp_hyp_dir, 'list1')
#     else:
#         latest_list_folder = max(list_folders, key=lambda x: int(x.name.replace('list', '')))
#         next_list_number = int(latest_list_folder.name.replace('list', '')) + 1
#         return os.path.join(temp_hyp_dir, f'list{next_list_number}')
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
        recall = last_row['      metrics/recall']
        return map50, map95, recall
    except KeyError as e:
        print(f"在DataFrame中找不到列: {e}")
        raise

    
def objective(trial, next_list_dir):
    # temp_hyp_dir = 'temp_hyp'
    # os.makedirs(temp_hyp_dir, exist_ok=True)
    # # 获取下一个list文件夹路径并创建
    # next_list_dir = get_next_list_folder(temp_hyp_dir)
    # os.makedirs(next_list_dir, exist_ok=True)

    # 为每个超参数定义搜索空间
    optimizer_choice = trial.suggest_categorical('optimizer', ['SGD', 'Adam'])
    lr0 = trial.suggest_loguniform('lr0_sgd', 1e-4, 1e-1) if optimizer_choice == 'SGD' else trial.suggest_loguniform('lr0_adam', 1e-5, 1e-2)
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
    lambda_ewc = trial.suggest_uniform('lambda_ewc', 0, 0.00001)
    mosaic = trial.suggest_uniform('mosaic', 1, 1)
    hsv_h= trial.suggest_uniform('hsv_h', 0.015  , 0.015  ) 
    hsv_s= trial.suggest_uniform('hsv_s', 0.7 , 0.7 ) 
    hsv_v= trial.suggest_uniform('hsv_v', 0.4 , 0.4 ) 
    degrees= trial.suggest_uniform('degrees', 0.0, 0.0)
    translate= trial.suggest_uniform('translate', 0.1, 0.1) 
    scale= trial.suggest_uniform('scale',0.9, 0.9) 
    shear= trial.suggest_uniform('shear', 0.0, 0.0) 
    perspective= trial.suggest_uniform('perspective', 0.0, 0.0)
    flipud= trial.suggest_uniform('flipud', 0.5 , 0.5 ) 
    fliplr= trial.suggest_uniform('fliplr', 0.5,0.5) 
    mixup= trial.suggest_uniform('mixup', 0.15, 0.15) 
    copy_paste= trial.suggest_uniform('copy_paste', 0.3, 0.3) 
    # 打印当前试验的超参数
    print(f"\nTrial parameters:\nOptimizer: {optimizer_choice}, lr0: {lr0}, momentum: {momentum}, lrf: {lrf}, "
          f"weight_decay: {weight_decay}, warmup_epochs: {warmup_epochs}, warmup_momentum: {warmup_momentum}, "
          f"warmup_bias_lr: {warmup_bias_lr}, box: {box}, cls: {cls}, cls_pw: {cls_pw}, obj: {obj}, obj_pw: {obj_pw}, "
          f"dfl: {dfl}, iou_t: {iou_t}, anchor_t: {anchor_t}, fl_gamma: {fl_gamma},lambda_ewc:{lambda_ewc}")

    # 创建临时超参数YAML文件
    hyp = deepcopy(locals())
    del hyp['trial']
    hyp_file = os.path.join(next_list_dir, f'hyp_trial_{trial.number}.yaml')
    with open(hyp_file, 'w') as f:
        yaml.dump(hyp, f, sort_keys=False)
    

    # 调用train.py进行训练
    command = f'python train_add.py --hyp {hyp_file}'
    subprocess.run(command, shell=True)
    
    # 查找最新的exp文件夹
    base_path = 'D:/code/yolov9-main/runs/train'
    latest_exp_folder = get_latest_exp_folder(base_path)
    # results_csv_path = os.path.join(latest_exp_folder, 'results.csv')
    f1_path = os.path.join(latest_exp_folder, 'f1_scores.txt')
    while not os.path.exists(f1_path):
        print("等待 f1_path...")
        time.sleep(10)  # 每10秒检查一次
    # map50, map95, recall = extract_map_from_results_csv(results_csv_path)
    f1 = calculate_f1(f1_path)
    f1_min =min(f1)
    print(f"Trial result: f1_min: {f1_min}")

    return f1_min

def print_best_trial(study, trial):
    # Optuna在每次试验后调用此函数
    print(f"\n当前最佳试验: {study.best_trial.number}")
    print(f"当前最佳值: {study.best_trial.value}")
    print(f"当前最佳参数: {study.best_trial.params}\n")


# def main():
#     temp_hyp_dir = 'temp_hyp'
#     os.makedirs(temp_hyp_dir, exist_ok=True)
#     # 获取下一个list文件夹路径并创建
#     next_list_dir = get_next_list_folder(temp_hyp_dir)
#     os.makedirs(next_list_dir, exist_ok=True)
#     study = optuna.create_study(direction='maximize')
#     # study.optimize(objective, n_trials=50)  # 修改n_trials为所需的试验次数
#     study.optimize(lambda trial: objective(trial, next_list_dir), n_trials=30)
#     print('已完成试验数:', len(study.trials))
#     print('最佳试验:', study.best_trial.params)
#     # print('Number of finished trials:', len(study.trials))
#     # best_trial = study.best_trial
#     # print(f'Best trial number: {best_trial.number}')
#     # print('Number of finished trials:', len(study.trials))
#     # print('Best trial:', study.best_trial.params)
#     # # 超参数重要性可视化并保存
#     # fig_param_importances = vis.plot_param_importances(study)
#     # fig_param_importances.write_image("vis/param_importances.png")

#     # # 优化历史可视化并保存
#     # fig_optimization_history = vis.plot_optimization_history(study)
#     # fig_optimization_history.write_image("vis/optimization_history.png")

#     # # 单个超参数性能可视化并保存
#     # fig_slice = vis.plot_slice(study)
#     # fig_slice.write_image("vis/slice.png")

#     try:
#         fig_param_importances = vis.plot_param_importances(study)
#         fig_param_importances.write_image("vis/param_importances.png")

#         fig_optimization_history = vis.plot_optimization_history(study)
#         fig_optimization_history.write_image("vis/optimization_history.png")

#         fig_slice = vis.plot_slice(study)
#         fig_slice.write_image("vis/slice.png")
#     except Exception as e:
#         print(f"发生错误：{e}")
#         traceback.print_exc()




# (其它函数定义保持不变)

def main():
    temp_hyp_dir = 'temp_hyp'
    os.makedirs(temp_hyp_dir, exist_ok=True)
    next_list_dir = get_next_list_folder(temp_hyp_dir)
    os.makedirs(next_list_dir, exist_ok=True)
    study = optuna.create_study(direction='maximize')
    
    study.optimize(lambda trial: objective(trial, next_list_dir), n_trials=20, callbacks=[print_best_trial])
   
    print('已完成试验数:', len(study.trials))
    print('最佳试验:', study.best_trial.params)

    try:
        # 使用plotly的方法直接渲染和保存图像
        fig_param_importances = optuna.visualization.plot_param_importances(study)
        fig_param_importances.write_image("vis/param_importances.png", engine="kaleido")
        fig_param_importances.show()

        fig_optimization_history = optuna.visualization.plot_optimization_history(study)
        fig_optimization_history.write_image("vis/optimization_history.png", engine="kaleido")
        fig_optimization_history.show()

        fig_slice = optuna.visualization.plot_slice(study)
        fig_slice.write_image("vis/slice.png", engine="kaleido")
        fig_slice.show()
    except Exception as e:
        print(f"发生错误：{e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()



if __name__ == '__main__':
    main()
