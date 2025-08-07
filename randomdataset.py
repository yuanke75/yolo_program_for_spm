import random

def merge_datasets(old_dataset_path, new_dataset_path, percentage):
    # 读取旧训练集地址
    with open(old_dataset_path, 'r') as file:
        old_data = file.readlines()
    
    # 读取新训练集地址
    with open(new_dataset_path, 'r') as file:
        new_data = file.readlines()
    
    # 计算应选取的旧数据数量
    num_to_select = int(len(old_data) * percentage / 100)
    
    # 随机选取旧数据
    selected_old_data = random.sample(old_data, num_to_select)
    
    # 合并新旧数据集
    merged_data = new_data + selected_old_data
    
    # 保存合并后的数据集地址列表（可选）
    with open(new_dataset_path, 'w') as file:
        for line in merged_data:
            file.write(line)
    
    print(f"Added {num_to_select} images from the old dataset to the new dataset.")

# 调用函数
old_dataset_path = "D:\\code\\yolov9-main\\datasetzzw\\voc\\ImageSets\\Main\\img_train.txt"
new_dataset_path = "D:\\code\\yolov9-main\\dataset030038\\voc\\ImageSets\\Main\\img_train.txt"
percentage = 8 # 例如，从旧数据集中随机选取20%

merge_datasets(old_dataset_path, new_dataset_path, percentage)
