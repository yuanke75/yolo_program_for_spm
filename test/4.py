#读取路径D:\code\yolov9-main\runs\train\exp38到D:\code\yolov9-main\runs\train\exp57共20个文件夹，每一个文件夹有一个results.csv，
#把所有20个results.csv复制出来粘贴到一个新文件夹中并且按照顺序重命名（比如D:\code\yolov9-main\runs\train\exp38中的results.csv就重命名为results38.csv）





import os
import shutil

# 设置源文件夹和目标文件夹路径
source_folder = 'D:/code/yolov9-main/runs/train'
destination_folder = 'D:/桌面/drawpic/results'  # 假设你想将文件复制到这个新文件夹

# 如果目标文件夹不存在，则创建它
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# 遍历exp38到exp57文件夹
for exp_num in range(46, 76):  # 58是因为range的结束值是不包含的
    # 构造当前exp文件夹的路径
    current_exp_folder = os.path.join(source_folder, f'exp{exp_num}')
    
    # 构造results.csv的原始路径
    original_csv_path = os.path.join(current_exp_folder, 'results.csv')
    
    # 构造目标路径，重命名文件
    destination_csv_path = os.path.join(destination_folder, f'results{exp_num}.csv')
    
    # 复制并重命名results.csv文件
    shutil.copyfile(original_csv_path, destination_csv_path)

print("所有results.csv文件已成功复制并重命名。")
