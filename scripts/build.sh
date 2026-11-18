#!/bin/bash
# 兼容旧用法:直接转给 build.py(Windows / macOS / Linux 通用,推荐直接用 build.py)。
#   bash <skill>/scripts/build.sh my_build.py 输出文件名 cn photo
#   PHONE="+65 8000 0000" JD=jd.txt bash <skill>/scripts/build.sh ...   # 环境变量写法仍然有效
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=$(command -v python3 || command -v python)
exec "$PY" "$DIR/build.py" "$@"
