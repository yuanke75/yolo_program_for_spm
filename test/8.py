#读取一个目录下所有的txt文件，每个txt文件有很多行组成，每一行有5个数，如果第一个数为0修改为2，如果第一个数为1修改为3


import os

# 指定包含.txt文件的目录路径
directory_path = 'D:/code/yolov9-main/datasetbestshuangzufen/voc/data/valid/labels'
# D:\code\yolov9-main\datasetbestshuangzufen
# 修改行中的第一个数字的函数
def modify_line(line):
    numbers = line.split()  # 将行分割成一个数字列表（字符串形式）
    if numbers:  # 检查行是否不为空
        if numbers[0] == '0':
            numbers[0] = '0'
        elif numbers[0] == '2':
            numbers[0] = '1'
        return ' '.join(numbers) + '\n'  # 将数字重新连接成字符串
    else:
        return '\n'

# 遍历目录中的所有文件
for filename in os.listdir(directory_path):
    if filename.endswith('.txt'):  # 检查文件是否为.txt文件
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r') as file:
            lines = file.readlines()  # 从文件中读取所有行

        # 根据规则修改每一行
        modified_lines = [modify_line(line) for line in lines]

        # 将修改后的行写回文件
        with open(file_path, 'w') as file:
            file.writelines(modified_lines)
