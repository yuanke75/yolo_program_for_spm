import torch

# 检查是否可以使用 CUDA
print("CUDA available: ", torch.cuda.is_available())

# 创建一个张量
x = torch.Tensor([1.0, 2.0, 3.0])
print("Tensor: ", x)
