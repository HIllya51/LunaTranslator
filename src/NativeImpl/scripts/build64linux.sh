#!/bin/bash
# Linux x64 构建（在WSL/Linux中运行），产物输出到 ../builds/Release_x64/
cd "$(dirname "$0")"

# 代理：构建中若CMakeLists有变动会触发重新configure，可能需要下载依赖
# WSL NAT模式下宿主机是默认网关，需在代理软件中开启“允许局域网连接”；
# 镜像网络模式、或WSL内本地代理，改成 http://127.0.0.1:7897 即可。
export http_proxy=http://$(ip route show default | awk '{print $3; exit}'):7897
export https_proxy=$http_proxy

cmake --build ../build/linux -j $(nproc)

# 部署到 files/DLL64（-a保留 .so 版本软链）
mkdir -p ../../files/DLL64
cp -a ../builds/Release_x64/*.so* ../../files/DLL64/
