#!/usr/bin/env bash

function PrepareVar(){
echo "onnxruntime: 1)CPU(默认), 2)GPU(cuda)"
read -p "" ONNX_TYPE
if [ $ONNX_TYPE == 1 ]; then
  ONNX_TYPE="CPU"
  GPU_INDEX=-1
elif [ $ONNX_TYPE == 2 ]; then
  ONNX_TYPE="CUDA"
  GPU_INDEX=0
else
  echo -e "输入错误！Input Error!"
fi
EXE_PATH=${sysOS}-${ONNX_TYPE}-BIN
}

sysOS=`uname -s`
NUM_THREADS=1
if [ $sysOS == "Darwin" ];then
    #echo "I'm MacOS"
    NUM_THREADS=$(sysctl -n hw.ncpu)
elif [ $sysOS == "Linux" ];then
    #echo "I'm Linux"
    NUM_THREADS=$(grep ^processor /proc/cpuinfo | wc -l)
else
    echo "Other OS: $sysOS"
fi

echo "Setting the Number of Threads=$NUM_THREADS Using an OpenMP Environment Variable"
set OMP_NUM_THREADS=$NUM_THREADS

PrepareVar

echo "请输入循环次数"
read -p "" LOOP_COUNT

TARGET_IMG=images/1.jpg
if [ ! -f "$TARGET_IMG" ]; then
echo "找不到待识别的目标图片：${TARGET_IMG}，请打开本文件并编辑TARGET_IMG"
exit
fi

./${EXE_PATH}/benchmark --version
./${EXE_PATH}/benchmark --models models \
--det ch_PP-OCRv3_det_infer.onnx \
--cls ch_ppocr_mobile_v2.0_cls_infer.onnx \
--rec ch_PP-OCRv3_rec_infer.onnx \
--keys ppocr_keys_v1.txt \
--image $TARGET_IMG \
--numThread $NUM_THREADS \
--padding 50 \
--maxSideLen 1024 \
--boxScoreThresh 0.5 \
--boxThresh 0.3 \
--unClipRatio 1.6 \
--doAngle 1 \
--mostAngle 1 \
--GPU $GPU_INDEX \
--loopCount $LOOP_COUNT