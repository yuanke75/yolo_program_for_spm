#需要你读取一个目录下的所有csv文件，把每个csv文件的第七列提取出来每一个第七列画一个折线图再把所有第七列的折线图合并成一个大图，图例用不同的颜色
# import pandas as pd
# import matplotlib.pyplot as plt

# # 读取CSV文件
# file_path = 'D:/code/yolov9-main/results/results48.csv'
# data = pd.read_csv(file_path)

# # 检查数据以确定第七列的标题
# column_title = data.columns[6]  # 第七列的标题

# # 提取第七列的数据
# data_series = data.iloc[:, 6]

# # 绘制折线图
# plt.figure(figsize=(10, 6))
# plt.plot(data_series, label=column_title)

# plt.xlabel('Epochs')  # 假设每个CSV文件都是5个时刻的数据
# plt.ylabel(column_title)
# plt.title(f'Time Series Data of {column_title}')
# plt.legend()
# plt.grid(True)
# plt.show()


import os
import pandas as pd
import matplotlib.pyplot as plt

# 假定你的CSV文件位于这个目录下
directory_path = 'D:/code/yolov9-main/results'

# 获取目录下所有的CSV文件
csv_files = [file for file in os.listdir(directory_path) if file.endswith('.csv')]

# 准备画图
plt.figure(figsize=(15, 10))

# 遍历每个CSV文件
for csv_file in csv_files:
    file_path = os.path.join(directory_path, csv_file)
    data = pd.read_csv(file_path)
    
    # 提取第七列的数据
    data_series = data.iloc[:, 7]
    
    # 为每个文件的第七列绘制折线图
    plt.plot(data_series, label=os.path.basename(file_path))
    
# 添加图例
plt.legend()

# 设置x轴和y轴的标签
plt.xlabel('Epochs')
plt.ylabel('Value')

# 设置图表标题
plt.title('Time Series Data of Column 8 from Multiple CSV Files')

# 显示网格
plt.grid(True)

# 显示图表
plt.show()
