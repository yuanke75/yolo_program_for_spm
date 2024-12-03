
#读取一个目录下的所有csv文件，将第一行中所有的/替换成_

import os
import csv

def replace_slashes_in_headers(directory):
    # 遍历目录下的所有文件
    for filename in os.listdir(directory):
        # 检查文件是否是CSV文件
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)
            
            # 确保文件不是空的
            if rows:
                # 替换第一行中的所有斜杠
                rows[0] = [header.replace(':', '_') for header in rows[0]]
            
            # 将修改后的内容写回到文件
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)

# 指定要处理的目录路径
directory = 'D:/桌面/drawpic/results'  # 请根据实际情况修改路径

# 执行函数
replace_slashes_in_headers(directory)

print("所有CSV文件的首行斜杠已成功替换为下划线。")
