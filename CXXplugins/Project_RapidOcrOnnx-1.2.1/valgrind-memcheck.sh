#!/bin/bash
## script for 内存泄露检查
# ========== macOS ==========
# https://github.com/LouisBrunner/valgrind-macos
# brew tap LouisBrunner/valgrind
# brew install --HEAD LouisBrunner/valgrind/valgrind
# ========== linux ==========
# https://www.valgrind.org/
# apt install valgrind

NUM_THREADS=1

set OMP_NUM_THREADS=$NUM_THREADS

TARGET_IMG=images/1.jpg
if [ ! -f "$TARGET_IMG" ]; then
echo "找不到待识别的目标图片：${TARGET_IMG}，请打开本文件并编辑TARGET_IMG"
exit
fi

sysOS=`uname -s`
EXE_PATH=${sysOS}-CPU-BIN

##### run test on MacOS or Linux
valgrind --tool=memcheck --leak-check=full --leak-resolution=med --track-origins=yes --vgdb=no --log-file=valgrind-memcheck.txt \
./${EXE_PATH}/RapidOcrOnnx --models models \
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
--GPU -1
