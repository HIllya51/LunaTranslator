#!/usr/bin/env bash

sysOS=$(uname -s)
NUM_THREADS=1
if [ $sysOS == "Darwin" ]; then
  #echo "I'm MacOS"
  NUM_THREADS=$(sysctl -n hw.nCPU)
elif [ $sysOS == "Linux" ]; then
  #echo "I'm Linux"
  NUM_THREADS=$(grep ^processor /proc/cpuinfo | wc -l)
else
  echo "Other OS: $sysOS"
fi

mkdir -p ${sysOS}-BIN-CPU
pushd ${sysOS}-BIN-CPU
cmake -DCMAKE_INSTALL_PREFIX=install -DCMAKE_BUILD_TYPE=Release -DOCR_OUTPUT="BIN" -DOCR_ONNX="CPU" ..
cmake --build . --config Release -j $NUM_THREADS
cmake --build . --config Release --target install
popd

mkdir -p ${sysOS}-JNI-CPU
pushd ${sysOS}-JNI-CPU
cmake -DCMAKE_INSTALL_PREFIX=install -DCMAKE_BUILD_TYPE=Release -DOCR_OUTPUT="JNI" -DOCR_ONNX="CPU" ..
cmake --build . --config Release -j $NUM_THREADS
cmake --build . --config Release --target install
popd

mkdir -p ${sysOS}-CLIB-CPU
pushd ${sysOS}-CLIB-CPU
cmake -DCMAKE_INSTALL_PREFIX=install -DCMAKE_BUILD_TYPE=Release -DOCR_OUTPUT="CLIB" -DOCR_ONNX="CPU" ..
cmake --build . --config Release -j $NUM_THREADS
cmake --build . --config Release --target install
popd