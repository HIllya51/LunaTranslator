#!/bin/bash
# Linux x64 配置（在WSL/Linux中运行，仅NativeUtils/CVUtils跨平台部分）
# 依赖：apt install build-essential cmake ninja-build git libopencv-dev protobuf-compiler libprotobuf-dev
cd "$(dirname "$0")"

# 代理：FetchContent下载github依赖需要。
# WSL NAT模式下宿主机是默认网关，需在代理软件中开启“允许局域网连接”；
# 镜像网络模式、或WSL内本地代理，改成 http://127.0.0.1:7897 即可。
export http_proxy=http://$(ip route show default | awk '{print $3; exit}'):7897
export https_proxy=$http_proxy

for cmd in cmake ninja protoc; do
    command -v $cmd >/dev/null || { echo "缺少 $cmd：apt install build-essential cmake ninja-build protobuf-compiler libopencv-dev libprotobuf-dev"; exit 1; }
done

cmake ../CMakeLists.txt -B ../build/linux -G Ninja -DCMAKE_BUILD_TYPE=Release "$@"
