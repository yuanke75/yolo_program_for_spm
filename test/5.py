#读取D:/code/yolov9-main/results中的csv文件，在每一个csv下创建一个其同样命名的子目录，在每个子目录中根据其相应命名的csv文件中的内容画折线图，（csv文件的样式跟上传文件一致），对于一个csv文件，每一列单独画一个折线图（第一列除外），保存为png图像，要求把列名作为x轴，y轴为epochs


import os
import pandas as pd
import matplotlib.pyplot as plt

def process_csv_and_generate_plots(csv_file_path):
    df = pd.read_csv(csv_file_path)
    
    base_name = os.path.splitext(os.path.basename(csv_file_path))[0]
    target_directory = os.path.join(os.path.dirname(csv_file_path), base_name)
    
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    
    epochs = df.iloc[:, 0]
    
    for column in df.columns[1:]:
        print(f"正在处理列: {column}")  # 调试打印
        
        plt.figure(figsize=(10, 6))
        plt.plot(epochs, df[column], label=column)
        plt.xlabel('Epochs')
        plt.ylabel(column)
        plt.title(f'{column} 随 Epochs 变化')
        plt.legend()
        plt.tight_layout()

        file_save_path = os.path.join(target_directory, f'{column}.png')
        print(f"保存图表到: {file_save_path}")  # 调试打印
        plt.savefig(file_save_path)
        plt.close()

source_folder = 'D:/code/yolov9-main/results'
for results_num in range(38, 58):
    csv_file_path = os.path.join(source_folder, f'results{results_num}.csv')

    # csv_file_path = 'D:/code/yolov9-main/results/results39.csv'
    process_csv_and_generate_plots(csv_file_path)

    print("处理完成。")
