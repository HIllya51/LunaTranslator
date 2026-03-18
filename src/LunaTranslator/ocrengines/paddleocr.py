import ast
import os
import subprocess
import tempfile

from language import Languages
from myutils.config import _TR
from ocrengines.baseocrclass import OCRResult, baseocr


class OCR(baseocr):
    def init(self):
        self.paddleocr_path = self.config.get("paddleocr_path", "")
        self.supportFilesPath = self.config.get("supportFilesPath", "")

    def langmap(self):
        return {
            Languages.Chinese: "ch",
            Languages.TradChinese: "chinese_cht",
            Languages.English: "en",
            Languages.Japanese: "japan",
            Languages.Korean: "korean",
        }

    def _resolve_model_dirs(self, lang, use_server_model, supportFilesPath):
        """解析模型目录"""
        if supportFilesPath and os.path.exists(supportFilesPath):
            base_path = supportFilesPath
        else:
            return None, None, None

        det_path = os.path.join(base_path, "det")
        rec_path = os.path.join(base_path, "rec")
        cls_path = os.path.join(base_path, "cls", "PP-LCNet_x1_0_textline_ori")

        mode = "server" if use_server_model else "mobile"

        # DET model selection
        if lang in {"ch", "chinese_cht", "en", "japan", "korean", "th", "el"}:
            det_sub = f"PP-OCRv5_{mode}_det"
        else:
            det_sub = "PP-OCRv3_mobile_det"

        # REC model selection
        if lang in ("ch", "chinese_cht", "japan"):
            rec_sub = f"PP-OCRv5_{mode}_rec"
        elif lang == "en":
            rec_sub = "en_PP-OCRv5_mobile_rec"
        elif lang == "korean":
            rec_sub = "korean_PP-OCRv5_mobile_rec"
        else:
            rec_sub = f"PP-OCRv5_{mode}_rec"

        return (
            os.path.join(det_path, det_sub),
            os.path.join(rec_path, rec_sub),
            cls_path,
        )

    def ocr(self, imagebinary):
        paddleocr_path = self.config.get("paddleocr_path", "")
        supportFilesPath = self.config.get("supportFilesPath", "")

        if not paddleocr_path or not os.path.isfile(paddleocr_path):
            raise Exception(_TR("未安装PaddleOCR或路径未配置"))

        lang = self.srclang
        lang = self.langmap().get(lang, "ch")
        use_gpu = self.config.get("use_gpu", False)
        use_angle_cls = self.config.get("use_angle_cls", False)
        use_server_model = self.config.get("use_server_model", False)
        conf_threshold = self.config.get("conf_threshold", 75)

        # 保存临时图片
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(imagebinary)
            tmp_path = tmp.name

        try:
            # 构建命令参数
            args = [
                paddleocr_path,
                "ocr",
                "--input",
                tmp_path,
                "--device",
                "gpu" if use_gpu else "cpu",
                "--use_textline_orientation",
                "true" if use_angle_cls else "false",
                "--use_doc_orientation_classify",
                "False",
                "--use_doc_unwarping",
                "False",
                "--lang",
                lang,
            ]

            # 添加模型目录
            det_model_dir, rec_model_dir, cls_model_dir = self._resolve_model_dirs(
                lang, use_server_model, supportFilesPath
            )
            if det_model_dir and os.path.exists(det_model_dir):
                args += ["--text_detection_model_dir", det_model_dir]
                args += ["--text_detection_model_name", os.path.basename(det_model_dir)]
            if rec_model_dir and os.path.exists(rec_model_dir):
                args += ["--text_recognition_model_dir", rec_model_dir]
                args += [
                    "--text_recognition_model_name",
                    os.path.basename(rec_model_dir),
                ]
            if cls_model_dir and use_angle_cls and os.path.exists(cls_model_dir):
                args += ["--textline_orientation_model_dir", cls_model_dir]
                args += [
                    "--textline_orientation_model_name",
                    os.path.basename(cls_model_dir),
                ]

            # 执行OCR
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                env=env,
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0 and stderr:
                raise Exception(f"PaddleOCR error: {stderr}")

            return self._parse_output(stdout, conf_threshold)

        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def _parse_output(self, stdout, conf_threshold):
        """解析PaddleOCR输出"""
        texts = []
        boxs = []

        for line in stdout.split("\n"):
            line = line.strip()
            if "ppocr INFO:" in line and "[[[" in line:
                idx = line.find("ppocr INFO:")
                if idx >= 0:
                    data_str = line[idx + 12 :].strip()
                    try:
                        ocr_data = ast.literal_eval(data_str)
                        # ocr_data 格式: [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ('text', confidence)]
                        if len(ocr_data) >= 2:
                            box = ocr_data[0]
                            text_info = ocr_data[1]

                            if (
                                isinstance(text_info, (list, tuple))
                                and len(text_info) >= 2
                            ):
                                text = str(text_info[0])
                                confidence = float(text_info[1])

                                if confidence * 100 >= conf_threshold and text.strip():
                                    texts.append(text)
                                    # 转换坐标格式: 4个角点 -> 8个值 (x1,y1,x2,y2,x3,y3,x4,y4)
                                    if len(box) == 4:
                                        box8 = []
                                        for point in box:
                                            box8.extend(point)
                                        boxs.append(box8)
                    except (ValueError, SyntaxError, IndexError):
                        continue

        if texts:
            return OCRResult(texts, boxs if boxs else None)

        return ""
