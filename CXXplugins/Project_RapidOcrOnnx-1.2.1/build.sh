#!/usr/bin/env bash

echo "========请先参考README.md准备好编译环境========"
echo

BUILD_TYPE=Release

BUILD_OUTPUT="BIN"

ONNX_TYPE="CPU"

sysOS=$(uname -s)
NUM_THREADS=1
if [ $sysOS == "Darwin" ]; then
  #echo "I'm MacOS"
  NUM_THREADS=$(sysctl -n hw.ncpu)
elif [ $sysOS == "Linux" ]; then
  #echo "I'm Linux"
  NUM_THREADS=$(grep ^processor /proc/cpuinfo | wc -l)
else
  echo "Other OS: $sysOS"
fi

mkdir -p $sysOS-$ONNX_TYPE-$BUILD_OUTPUT
pushd $sysOS-$ONNX_TYPE-$BUILD_OUTPUT

echo "cmake -DCMAKE_INSTALL_PREFIX=install -DCMAKE_BUILD_TYPE=$BUILD_TYPE -DOCR_OUTPUT=$BUILD_OUTPUT -DOCR_ONNX=$ONNX_TYPE .."
cmake -DCMAKE_INSTALL_PREFIX=install -DCMAKE_BUILD_TYPE=$BUILD_TYPE -DOCR_OUTPUT=$BUILD_OUTPUT -DOCR_ONNX=$ONNX_TYPE ..
cmake --build . --config $BUILD_TYPE -j $NUM_THREADS
cmake --build . --config $BUILD_TYPE --target install
popd
