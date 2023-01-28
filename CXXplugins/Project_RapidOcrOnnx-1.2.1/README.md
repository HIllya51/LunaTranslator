# RapidOcrOnnx

### 联系方式

* QQ①群：887298230

### Project下载

* 整合好源码和依赖库的完整工程项目，可以在Release中下载(github)
* 可到Q群共享内下载，以Project开头的压缩包文件为源码工程，例：Project_RapidOcrOnnx-版本号.7z
* 如果想自己折腾，则请继续阅读本说明

### Demo下载(win、mac、linux)

* 编译好的demo，可以在release中下载，或者Q群共享内下载
* 各平台可执行文件：linux-bin.7z、macos-bin.7z、windows-bin.7z
* 用于java的jni库：linux-jni.7z、macos-jni.7z、windows-jni.7z
* 用于C的动态库：linux-clib.7z、macos-clib.7z、windows-clib.7z
* C动态库调用范例:[RapidOcrOnnxLibTest](https://github.com/RapidAI/RapidOcrOnnxLibTest)
* 注意：linux编译平台为ubuntu18.04，如果你的linux版本无法运行demo，请自行从源码编译依赖库和完整项目。

### 介绍

请查看项目主仓库：https://github.com/RapidAI/RapidOCR

这个项目使用onnxruntime框架进行推理

采用onnxruntime框架[https://github.com/microsoft/onnxruntime](https://github.com/microsoft/onnxruntime)

### 更新说明

#### 2021-10-15 update

* opencv 4.6.0
* onnxruntime 1.12.1
* windows支持mt版引用库
* rec模型输入图片高度改为48

#### 2021-10-16 update

* 修复：字典添加空格

#### 2021-10-17 update

* 修复：scoreToTextLine方法索引越界问题
* Windows控制台编码修改为UTF8

#### 2021-10-20 update

* 再次修复空格问题
* 增加GPU(cuda)支持，需要自行下载整合依赖库
* windows下的free()方法更焕为_aligned_free()
* 修改默认输入参数
* 修改benchmark输出样式

#### 2021-10-28 update

* 适配onnxruntime 1.13.1
* 修了些warning

### 模型下载

整合好的范例工程自带了模型，在models文件夹中

```
RapidOcrOnnx/models
    ├── ch_PP-OCRv3_det_infer.onnx
    ├── ch_PP-OCRv3_rec_infer.onnx
    ├── ch_ppocr_mobile_v2.0_cls_infer.onnx
    └── ppocr_keys_v1.txt
```

### [编译说明](./BUILD.md)

### [GPU版附加说明](./onnxruntime-gpu/README.md)

### 测试说明

1. 根据系统下载对应的程序包linux-bin.7z、macos-bin.7z、windows-bin.7z，并解压.
2. 把上面的模型下载，解压到第一步解压的文件夹里.
3. 终端运行run-test.sh或命令行运行run-test.bat，查看识别结果.
4. 终端运行run-benchmark.sh或命令行运行run-benchmark.bat，查看识别过程平均耗时.

### FAQ

#### windows静态链接msvc

- 作用:静态链接CRT(mt)可以让编译出来的包，部署时不需要安装c++运行时，但会增大包体积；
- 需要mt版的引用库，参考编译说明，下载mt版的库；

#### windows提示缺少"VCRUNTIME140_1.dll"

下载安装适用于 Visual Studio 2015、2017 和 2019 的 Microsoft Visual C++ 可再发行软件包
[下载地址](https://support.microsoft.com/zh-cn/help/2977003/the-latest-supported-visual-c-downloads)

#### Windows7执行错误|中文乱码

1. cmd窗口左上角-属性
2. 字体选项卡-选择除了“点阵字体”以外的TrueType字体,例如:Lucida Console、宋体
3. 重新执行bat

### Windows调试运行

* 下载范例项目工程自带的引用库是Release版，不能用于调试运行
* debug版的引用库未压缩时容量超过1GB，极限压缩后也超过了100MB，请自行编译或到群共享里寻找
* debug版的引用库必须是md版
* 把debug版的引用库替换到范例工程的对应文件夹
* 双击generate-vs-project.bat，选择2)Debug，生成对应的build-win-vsxxx-xx文件夹
* 进入生成的文件夹，打开RapidOcrOnnx.sln
* 右边解决方案管理器，选中RapidOcrOnnx，右键->设为启动项目，并生成(查看输出log，确保生成成功)
* 如果引用库是dll，需要把对应的dll文件，例onnxruntime.dll复制到build-win-vsxxx-xx文件夹\Debug，跟上一步生成的RapidOcrOnnx.exe放在一起
* 右边解决方案管理器，选中RapidOcrOnnx，右键->属性->调试->
  命令参数->```--models ../models --det ch_PP-OCRv3_det_infer.onnx --cls ch_ppocr_mobile_v2.0_cls_infer.onnx --rec ch_PP-OCRv3_rec_infer.onnx --keys ppocr_keys_v1.txt --image ../images/1.jpg```
* 工具栏，点击绿色三角号启动"本地Windows调试器"
* 第一次运行的话，查看左下角，等待加载各dll符号，网络不好的话，要等挺久的

### 输入参数说明

* 请参考main.h中的命令行参数说明。
* 每个参数有一个短参数名和一个长参数名，用短的或长的均可。

1. ```-d或--models```：模型所在文件夹路径，可以相对路径也可以绝对路径。
2. ```-1或--det```:det模型文件名(含扩展名)
3. ```-2或--cls```:cls模型文件名(含扩展名)
4. ```-3或--rec```:rec模型文件名(含扩展名)
5. ```-4或--keys```:keys.txt文件名(含扩展名)
6. ```-i或--image```：目标图片路径，可以相对路径也可以绝对路径。
7. ```-t或--numThread```：线程数量。
8. ```-p或--padding```：图像预处理，在图片外周添加白边，用于提升识别率，文字框没有正确框住所有文字时，增加此值。
9. ```-s或--maxSideLen```
   ：按图片最长边的长度，此值为0代表不缩放，例：1024，如果图片长边大于1024则把图像整体缩小到1024再进行图像分割计算，如果图片长边小于1024则不缩放，如果图片长边小于32，则缩放到32。
10. ```-b或--boxScoreThresh```：文字框置信度门限，文字框没有正确框住所有文字时，减小此值。
11. ```-o或--boxThresh```：请自行试验。
12. ```-u或--unClipRatio```：单个文字框大小倍率，越大时单个文字框越大。此项与图片的大小相关，越大的图片此值应该越大。
13. ```-a或--doAngle```：启用(1)/禁用(0) 文字方向检测，只有图片倒置的情况下(旋转90~270度的图片)，才需要启用文字方向检测。
14. ```-A或--mostAngle```：启用(1)/禁用(0) 角度投票(整张图片以最大可能文字方向来识别)，当禁用文字方向检测时，此项也不起作用。
15. ```-h或--help```：打印命令行帮助。

### 关于内存泄漏与valgrind

* 项目根目录的valgrind-memcheck.sh用来检查内存泄漏(需要debug编译)。
* 常见的并行库有tbb，hpx，openmp，gcd，concurrency，pthread
* 并行库的种类可以看：https://docs.opencv.org/4.x/db/d05/tutorial_config_reference.html
* 测试了openmp和pthread，目前已知这类并行库会导致检查报告中出现"possibly lost"
* opencv只做简单的图像预处理，可以完全不使用任何并行库，但需要定制编译
* onnxruntime1.6.0或之前，默认引用openmp，从1.7.0开始默认关闭openmp并使用自带的ThreadPool代码
* 阅读报告可以看出"possibly lost"发生位置均在引用的第三方库(如果使用了并行库的话)，如opencv或onnxruntime
* "possibly lost"不一定是内存泄露
* 如果opencv想定制编译不使用任何并行库，可以使用以下参数进行编译

```
-DWITH_TBB=OFF
-DWITH_HPX=OFF
-DWITH_OPENMP=OFF
-DWITH_GCD=OFF
-DWITH_CONCURRENCY=OFF
-DWITH_PTHREADS_PF=OFF
```