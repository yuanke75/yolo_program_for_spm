#帮我写一段代码，要求检索一个目录下包括其子目录的所有txt文件和jpg文件，如果txt文件或jpg文件以de为结尾就删除其余保存

import os
import glob

def delete_files_except_de_ending(directory):
    # 遍历目录及其所有子目录
    for root, dirs, files in os.walk(directory):
        # 在当前目录下找到所有.txt和.jpg文件
        for ext in ('*.txt', '*.jpg' , '*.xml'):
            for file in glob.glob(os.path.join(root, ext)):
                # 检查文件名是否以'de'结尾
                if not file.endswith('de'):
                    # 不以'de'结尾的文件将被删除
                    os.remove(file)
                    print(f"Deleted: {file}")
                else:
                    # 以'de'结尾的文件将被保留
                    print(f"Kept: {file}")

# 调用函数，你需要将'directory_path'替换为你的目录路径
delete_files_except_de_ending('D:/code/yolov9-main/dataset/voc')
