#读取一个txt文件检索其中每一行把yolov7-pose_Npoint_Ncla-master替换成yolov9-main

def replace_string_in_file(file_path, original_string, new_string):
    # 打开文件读取内容
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # 替换每一行中的字符串
    modified_lines = [line.replace(original_string, new_string) for line in lines]
    # 将修改后的内容写回文件
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

# 调用函数，替换以下路径为你的实际文件路径
file_path = 'D:/code/yolov9-main/datasetbestshuangzufen/voc/ImageSets/Main/img_valid.txt'
replace_string_in_file(file_path, 'dataset', 'datasetbestshuangzufen')
