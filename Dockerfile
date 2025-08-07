# 使用一个基础的Anaconda映像
FROM continuumio/anaconda3

# 设置工作目录
WORKDIR /opt/conda/envs

# 复制环境压缩包到工作目录
COPY yolotest.tar.gz .

# 解压压缩包
RUN tar -xzf yolotest.tar.gz

# 复制项目目录到容器中
COPY . /opt/conda/envs/yolotest

# 安装必要的系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libegl1-mesa \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libxi6 \
    libxtst6

# 激活环境
RUN echo "source activate yolotest" > ~/.bashrc
ENV PATH /opt/conda/envs/yolotest/bin:$PATH

# 安装 Python 依赖
RUN /opt/conda/envs/yolotest/bin/pip install imgaug

# 设置工作目录为解压后的环境目录
WORKDIR /opt/conda/envs/yolotest

# 设置默认命令
CMD ["/bin/bash"]
