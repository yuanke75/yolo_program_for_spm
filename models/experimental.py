import math

import numpy as np
import torch
import torch.nn as nn

from utils.downloads import attempt_download


class Sum(nn.Module):
    # Weighted sum of 2 or more layers https://arxiv.org/abs/1911.09070
    def __init__(self, n, weight=False):  # n: number of inputs
        super().__init__()
        self.weight = weight  # apply weights boolean
        self.iter = range(n - 1)  # iter object
        if weight:
            self.w = nn.Parameter(-torch.arange(1.0, n) / 2, requires_grad=True)  # layer weights

    def forward(self, x):
        y = x[0]  # no weight
        if self.weight:
            w = torch.sigmoid(self.w) * 2
            for i in self.iter:
                y = y + x[i + 1] * w[i]
        else:
            for i in self.iter:
                y = y + x[i + 1]
        return y


class MixConv2d(nn.Module):
    # Mixed Depth-wise Conv https://arxiv.org/abs/1907.09595
    def __init__(self, c1, c2, k=(1, 3), s=1, equal_ch=True):  # ch_in, ch_out, kernel, stride, ch_strategy
        super().__init__()
        n = len(k)  # number of convolutions
        if equal_ch:  # equal c_ per group
            i = torch.linspace(0, n - 1E-6, c2).floor()  # c2 indices
            c_ = [(i == g).sum() for g in range(n)]  # intermediate channels
        else:  # equal weight.numel() per group
            b = [c2] + [0] * n
            a = np.eye(n + 1, n, k=-1)
            a -= np.roll(a, 1, axis=1)
            a *= np.array(k) ** 2
            a[0] = 1
            c_ = np.linalg.lstsq(a, b, rcond=None)[0].round()  # solve for equal weight indices, ax = b

        self.m = nn.ModuleList([
            nn.Conv2d(c1, int(c_), k, s, k // 2, groups=math.gcd(c1, int(c_)), bias=False) for k, c_ in zip(k, c_)])
        self.bn = nn.BatchNorm2d(c2)
        self.act = nn.SiLU()

    def forward(self, x):
        return self.act(self.bn(torch.cat([m(x) for m in self.m], 1)))


class Ensemble(nn.ModuleList):
    # Ensemble of models
    def __init__(self):
        super().__init__()

    def forward(self, x, augment=False, profile=False, visualize=False):
        y = [module(x, augment, profile, visualize)[0] for module in self]
        # y = torch.stack(y).max(0)[0]  # max ensemble
        # y = torch.stack(y).mean(0)  # mean ensemble
        y = torch.cat(y, 1)  # nms ensemble
        return y, None  # inference, train output


def attempt_load(weights, device=None, inplace=True, fuse=True):
    # Loads an ensemble of models weights=[a,b,c] or a single model weights=[a] or weights=a
    from models.yolo import Detect, Model

    model = Ensemble()
    for w in weights if isinstance(weights, list) else [weights]:
        ckpt = torch.load(attempt_download(w), map_location='cpu')  # load

        # ckpt = (ckpt.get('ema') or ckpt['model']).to(device).float()  # FP32 model
        ckpt =  ckpt['model'].to(device).float()  # FP32 model
        # Model compatibility updates
        if not hasattr(ckpt, 'stride'):
            ckpt.stride = torch.tensor([32.])
        if hasattr(ckpt, 'names') and isinstance(ckpt.names, (list, tuple)):
            ckpt.names = dict(enumerate(ckpt.names))  # convert to dict

        model.append(ckpt.fuse().eval() if fuse and hasattr(ckpt, 'fuse') else ckpt.eval())  # model in eval mode

    # Module compatibility updates
    for m in model.modules():
        t = type(m)
        if t in (nn.Hardswish, nn.LeakyReLU, nn.ReLU, nn.ReLU6, nn.SiLU, Detect, Model):
            m.inplace = inplace  # torch 1.7.0 compatibility
            # if t is Detect and not isinstance(m.anchor_grid, list):
            #    delattr(m, 'anchor_grid')
            #    setattr(m, 'anchor_grid', [torch.zeros(1)] * m.nl)
        elif t is nn.Upsample and not hasattr(m, 'recompute_scale_factor'):
            m.recompute_scale_factor = None  # torch 1.11.0 compatibility

    # Return model
    if len(model) == 1:
        return model[-1]

    # Return detection ensemble
    print(f'Ensemble created with {weights}\n')
    for k in 'names', 'nc', 'yaml':
        setattr(model, k, getattr(model[0], k))
    model.stride = model[torch.argmax(torch.tensor([m.stride.max() for m in model])).int()].stride  # max stride
    assert all(model[0].nc == m.nc for m in model), f'Models have different class counts: {[m.nc for m in model]}'
    return model



# def attempt_load(weights, device=None, inplace=True, fuse=True):
#     # Loads an ensemble of models weights=[a,b,c] or a single model weights=[a] or weights=a
#     model = Ensemble()
#     for w in weights if isinstance(weights, list) else [weights]:
#         ckpt = torch.load(attempt_download(w), map_location='cpu')  # load
#         ckpt_model = ckpt.get('ema') or ckpt.get('model')  # 获取模型权重

#         # 创建一个新的模型实例
#         model_instance = Model()  # 假设你有一个叫做Model的模型类
#         model_instance.load_state_dict(ckpt_model)  # 加载权重
#         model_instance = model_instance.to(device).float()  # 转移到指定的设备，转换为float32

#         # 模型兼容性更新
#         if not hasattr(model_instance, 'stride'):
#             model_instance.stride = torch.tensor([32.])
#         if hasattr(model_instance, 'names') and isinstance(model_instance.names, (list, tuple)):
#             model_instance.names = dict(enumerate(model_instance.names))  # 转换为字典

#         model.append(model_instance.fuse().eval() if fuse and hasattr(model_instance, 'fuse') else model_instance.eval())  # 加入模型，设置为评估模式

#     # 模块兼容性更新
#     for m in model.modules():
#         t = type(m)
#         if t in (nn.Hardswish, nn.LeakyReLU, nn.ReLU, nn.ReLU6, nn.SiLU, Detect):
#             m.inplace = inplace  # torch 1.7.0 兼容性
#         elif t is nn.Upsample and not hasattr(m, 'recompute_scale_factor'):
#             m.recompute_scale_factor = None  # torch 1.11.0 兼容性

#     return model  # 返回模型集合
# def attempt_load(weights, device=None, inplace=True, fuse=True):
#     from models.yolo import Model  # 确保这是你的模型定义

#     model = None
#     for w in weights if isinstance(weights, list) else [weights]:
#         ckpt = torch.load(w, map_location='cpu')  # 加载权重文件
        
#         # 确定使用 'ema' 还是 'model' 键
#         state_dict = ckpt.get('ema') or ckpt.get('model')
#         if state_dict is None:
#             raise KeyError("Checkpoint does not contain 'ema' or 'model' state_dict")
        
#         # 如果尚未创建模型实例，则创建它
#         if model is None:
#             model = Model().to(device)  # 创建模型实例并将其移到指定的设备
#         model.load_state_dict(state_dict)  # 加载状态字典

#     model.float()  # 确保模型为 FP32
#     model.eval()  # 设置为评估模式

#     if fuse:
#         # 如果你的模型有 fuse 方法并且你想要在加载后立即使用它
#         try:
#             model.fuse()
#         except AttributeError as e:
#             print(f"Model doesn't have 'fuse' method, skipping... ({e})")

#     return model
