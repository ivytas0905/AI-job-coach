#!/bin/bash
# 告诉系统这是一个 bash 脚本

# 1. 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    python3 -m venv venv  # 不存在就创建
fi

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 如果加了 --install 参数，或者 pip 不存在，就安装依赖
if [ "$1" = "--install" ] || [ ! -f "venv/bin/pip" ]; then
    pip install -r requirements.txt
fi

# 4. 检查 .env 配置文件是否存在
if [ ! -f ".env" ]; then
    echo "错误：找不到 .env 文件"
    exit 1  # 退出脚本
fi

# 5. 创建上传和日志目录
mkdir -p uploads logs

# 6. 启动 Python 服务
python -m src.agent_service.main

