 
import sys
from traceback import print_exc 
import numpy as np
from utils.config import globalconfig 
import time 
from utils.wrapper import timer
import math
from ocr.recpost import process_pred
import cv2
from ocr.detpost import DBPostProcess
import onnxruntime
def traditional_image_processing(image):
    # 转化成灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
    #使用锐化操作，突出图像的高频特征，好像没啥用处
    #gray = cv2.filter2D(gray, -1,kernel=np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32))  # 对图像进行滤波,是锐化操作
    #gray = cv2.filter2D(gray, -1, kernel=np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32))
 
    # 利用Sobel边缘检测生成二值图
    sobel = cv2.Sobel(gray, cv2.CV_8U, 0, 1, ksize=3) 
    #gradY = cv2.Sobel(sobel, ddepth=cv2.CV_8U, dx=0, dy=1,ksize=3)
    #sobel = cv2.subtract(sobel, gradY)  # 使用减法作图像融合？
    # 二值化
    ret, binary = cv2.threshold(sobel, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
 
    # 膨胀、腐蚀
    element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 9))
    element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (24, 6))
 
    # 膨胀一次，让轮廓突出
    dilation = cv2.dilate(binary, element2, iterations=1)
 
    # 腐蚀一次，去掉细节
    erosion = cv2.erode(dilation, element1, iterations=1)
 
    # 再次膨胀，让轮廓明显一些
    dilation2 = cv2.dilate(erosion, element2, iterations=2)
 
    #  查找轮廓和筛选文字区域
    region = []
    _,contours, hierarchy = cv2.findContours(dilation2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(len(contours)):
        cnt = contours[i]
 
        # 计算轮廓面积，并筛选掉面积小的
        area = cv2.contourArea(cnt)
        if (area < 1000):
            continue
 
        # 找到最小的矩形
        rect = cv2.minAreaRect(cnt) 
 
        # box是四个点的坐标
        box = cv2.boxPoints(rect)
        box = np.int0(box)
 
        # 计算高和宽
        height = abs(box[0][1] - box[2][1])
        width = abs(box[0][0] - box[2][0])
 
        # 根据文字特征，筛选那些太细的矩形，留下扁的
        if (height > width * 1.3):
            continue
        xmin=min(box[:,0])
        xmax=max(box[:,0])
        ymin=min(box[:,1])
        ymax=max(box[:,1])
        region.append([xmin,ymin,xmax,ymax])
     

        
    #     cv2.drawContours(image, [box], 0, (0, 255, 0), 2)
 
    # cv2.imshow('img', image) 
    return region
    #

def fastdet(imgr):
     
    img=cv2.cvtColor(imgr,cv2.COLOR_BGR2GRAY)
    img=np.float32(img) 
    r2=cv2.cornerHarris(img,2,3,0.04)  
    savedst=r2.copy()
    two=np.zeros_like(r2)
    two[savedst>0.001*savedst.max()]=1  
    h,w=r2.shape 
    count=np.sum(two,axis=1) 
    _h=0 
    filed=[]
    while _h<h:
        while _h<h and count[_h]<10:
            _h+=1
        start=_h
        while _h<h and count[_h]>=10:
            _h+=1
        end=_h
        filed.append([start,end])  
    lines=[] 
    for ff in filed:
        if ff[1]-ff[0]>20:
            lineimg=imgr[ff[0]:ff[1]]
            lines.append([ff,lineimg])
            #cv2.imshow(str(ff[0]),lineimg) 
    smallimg=[]

    for line in lines:
        small=traditional_image_processing(line[1]) 
        
        if len(small)==0:
            smallimg.append(line[1])
        else:
             
            xmin=9999
            xmax=0 
            for ss in small:
                xmin=min(xmin,ss[0]) 
                xmax=max(xmax,ss[2])  
            smallimg.append([xmin,line[0][0],xmax,line[0][1]])
    return smallimg
class NormalizeImage(object):
    """ normalize image such as substract mean, divide std
    """

    def __init__(self, scale=None, mean=None, std=None, order='chw', **kwargs):
        if isinstance(scale, str):
            scale = eval(scale)
        self.scale = np.float32(scale if scale is not None else 1.0 / 255.0)
        mean = mean if mean is not None else [0.485, 0.456, 0.406]
        std = std if std is not None else [0.229, 0.224, 0.225]

        shape = (3, 1, 1) if order == 'chw' else (1, 1, 3)
        self.mean = np.array(mean).reshape(shape).astype('float32')
        self.std = np.array(std).reshape(shape).astype('float32')

    def __call__(self, data):
        img = data['image']
         

        assert isinstance(img,
                          np.ndarray), "invalid input 'img' in NormalizeImage"
        data['image'] = (
            img.astype('float32') * self.scale - self.mean) / self.std
        return data


class ToCHWImage(object):
    """ convert hwc image to chw image
    """

    def __init__(self, **kwargs):
        pass

    def __call__(self, data):
        img = data['image']
        
        data['image'] = img.transpose((2, 0, 1))
        return data
 

class KeepKeys(object):
    def __init__(self, keep_keys, **kwargs):
        self.keep_keys = keep_keys

    def __call__(self, data):
        data_list = []
        for key in self.keep_keys:
            data_list.append(data[key])
        return data_list

class DetResizeForTest(object):
    def __init__(self, **kwargs):
        super(DetResizeForTest, self).__init__()
        self.resize_type = 0
        self.limit_side_len = kwargs['limit_side_len']
        self.limit_type = kwargs.get('limit_type', 'min')

    def __call__(self, data):
        img = data['image']
        src_h, src_w, _ = img.shape
        img, [ratio_h, ratio_w] = self.resize_image_type0(img)
        data['image'] = img
        data['shape'] = np.array([src_h, src_w, ratio_h, ratio_w])
        return data

    def resize_image_type0(self, img):
        """
        resize image to a size multiple of 32 which is required by the network
        args:
            img(array): array with shape [h, w, c]
        return(tuple):
            img, (ratio_h, ratio_w)
        """
        limit_side_len = self.limit_side_len
        h, w, _ = img.shape

        # limit the max side
        if max(h, w) > limit_side_len:
            if h > w:
                ratio = float(limit_side_len) / h
            else:
                ratio = float(limit_side_len) / w
        else:
            ratio = 1.
        resize_h = int(h * ratio)
        resize_w = int(w * ratio)


        resize_h = int(round(resize_h / 32) * 32)
        resize_w = int(round(resize_w / 32) * 32)

    
        if int(resize_w) <= 0 or int(resize_h) <= 0:
            return None, (None, None)
        img = cv2.resize(img, (int(resize_w), int(resize_h)))
        
        ratio_h = resize_h / float(h)
        ratio_w = resize_w / float(w)
       # print(img.shape)
        # return img, np.array([h, w])
        return img, [ratio_h, ratio_w]

def mydetect(imgr):
    #small1=traditional_image_processing(imgr) 
    small2=fastdet(imgr)
     
    # for small in small1:
    #     if len(small2)>0:
    #         if small[3]-small[1]<0.8*(small2[0][3]-small2[0][1]):
    #             continue
    #     al=1
    #     for small22 in small2:
    #         iou=cal_iou(small22,small)
    #         if iou>0:
    #             al=0
    #             break
    #     if al==1:

    #         small2.append(small)
    small2.sort(key=lambda x:x[1])
    return small2
def simplecrop(img,boxs):
    ss=[]
    for box in boxs:
        ss.append(img[box[1]:box[3],box[0]:box[2]])
    return ss
import os
class myocr:
    
    def __init__(self) -> None: 
        self.large_rec_file = os.path.join('./files/ocr','2.0jprec.onnx')
        #self.large_rec_file2 = os.path.join('./files/ocr','en.onnx')
        self.det_file = os.path.join('./files/ocr','2.6chdet.onnx')  
        self.onet_rec_session = onnxruntime.InferenceSession(self.large_rec_file)
        #self.onet_rec_session_en = onnxruntime.InferenceSession(self.large_rec_file2)
        self.onet_det_session = onnxruntime.InferenceSession(self.det_file)
        self.postprocess_op = process_pred(os.path.join('./files/ocr','japan_dict.txt'),   True) 
        #self.postprocess_op_en = process_pred(os.path.join('./files/ocr','en_dict.txt'),   True) 
        self.infer_before_process_op, self.det_re_process_op = self.get_process()
        self.statistic=[]
    def recognition_img_croped(self,img_list):
        results = []
        for pic in img_list:
            # cv2.imshow(str(time.time()),pic)
            # cv2.waitKey()
            res = self.get_img_res(self.onet_rec_session, pic, self.postprocess_op)
            # if globalconfig['srclang']==0:
            #     res = self.get_img_res(self.onet_rec_session, pic, self.postprocess_op)
            # elif globalconfig['srclang']==1:
            #     res = self.get_img_res(self.onet_rec_session_en, pic, self.postprocess_op_en)
            results.append(res)
        #
        return  results
    def resize_norm_img(self, img, max_wh_ratio):
        imgC, imgH, imgW = [int(v) for v in "3, 32, 100".split(",")]
        assert imgC == img.shape[2]
        H=48
        imgW = int((H * max_wh_ratio))
        h, w = img.shape[:2]
        ratio = w / float(h)
        if math.ceil(imgH * ratio) > imgW:
            resized_w = imgW
        else:
            resized_w = int(math.ceil(imgH * ratio)) 
        resized_image = cv2.resize(img, (resized_w, H))
        resized_image = resized_image.astype('float32')
        resized_image = resized_image.transpose((2, 0, 1)) / 255
        resized_image -= 0.5
        resized_image /= 0.5
         
        return resized_image
     
    def transform(self, data, ops=None):
        """ transform """
        if ops is None:
            ops = []
        for op in ops:
            data = op(data)
            if data is None:
                return None
        return data
    def get_process(self):
        det_db_thresh = 0.3
        det_db_box_thresh = 0.5
        max_candidates = 2000
        unclip_ratio = 1.6
        use_dilation = True

        pre_process_list = [{
            'DetResizeForTest': {
                'limit_side_len': 2500,
                'limit_type': 'max'
            }
        }, {
            'NormalizeImage': {
                'std': [0.229, 0.224, 0.225],
                'mean': [0.485, 0.456, 0.406],
                'scale': '1./255.',
                'order': 'hwc'
            }
        }, {
            'ToCHWImage': None
        }, {
            'KeepKeys': {
                'keep_keys': ['image', 'shape']
            }
        }]

        infer_before_process_op = self.create_operators(pre_process_list)
        det_re_process_op = DBPostProcess(det_db_thresh, det_db_box_thresh, max_candidates, unclip_ratio, use_dilation)
        return infer_before_process_op, det_re_process_op
    def create_operators(self, op_param_list, global_config=None):
        """
        create operators based on the config

        Args:
            params(list): a dict list, used to create some operators
        """
        assert isinstance(op_param_list, list), ('operator config should be a list')
        ops = []
        for operator in op_param_list:
            assert isinstance(operator,
                              dict) and len(operator) == 1, "yaml format error"
            op_name = list(operator)[0]
            param = {} if operator[op_name] is None else operator[op_name]
            if global_config is not None:
                param.update(global_config)
            op = eval(op_name)(**param)
            ops.append(op)
        return ops
    def get_boxes(self,img):
        img_ori =  img
        img_part = img_ori.copy()
        data_part = {'image': img_part}
        data_part = self.transform(data_part, self.infer_before_process_op)
        img_part, shape_part_list = data_part
        img_part = np.expand_dims(img_part, axis=0)
        shape_part_list = np.expand_dims(shape_part_list, axis=0)

        inputs_part = {self.onet_det_session.get_inputs()[0].name: img_part}
        outs_part = self.onet_det_session.run(None, inputs_part)
        post_res_part = self.det_re_process_op(outs_part[0], shape_part_list)

        dt_boxes_part = post_res_part[0]['points']
        dt_boxes_part = self.filter_tag_det_res(dt_boxes_part, img_ori.shape) 
        return dt_boxes_part 
    def order_points_clockwise(self, pts):
        """
        reference from: https://github.com/jrosebr1/imutils/blob/master/imutils/perspective.py
        # sort the points based on their x-coordinates
        """
        xSorted = pts[np.argsort(pts[:, 0]), :]

        # grab the left-most and right-most points from the sorted
        # x-roodinate points
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:, :]

        # now, sort the left-most coordinates according to their
        # y-coordinates so we can grab the top-left and bottom-left
        # points, respectively
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        (tl, bl) = leftMost

        rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
        (tr, br) = rightMost

        rect = np.array([tl, tr, br, bl], dtype="float32")
        return rect

    def clip_det_res(self, points, img_height, img_width):
        for pno in range(points.shape[0]):
            points[pno, 0] = int(min(max(points[pno, 0], 0), img_width - 1))
            points[pno, 1] = int(min(max(points[pno, 1], 0), img_height - 1))
        return points

    def filter_tag_det_res(self, dt_boxes, image_shape):
        img_height, img_width = image_shape[0:2]
        dt_boxes_new = []
        for box in dt_boxes:
            box = self.order_points_clockwise(box)
            box = self.clip_det_res(box, img_height, img_width)
            rect_width = int(np.linalg.norm(box[0] - box[1]))
            rect_height = int(np.linalg.norm(box[0] - box[3]))
            if rect_width <= 3 or rect_height <= 3:
                continue
            dt_boxes_new.append(box)
        dt_boxes = np.array(dt_boxes_new)
        return dt_boxes

    def get_img_res(self, onnx_model, img, process_op):
        
        h, w = img.shape[:2]
         
        img = self.resize_norm_img(img, w * 1.0 / h)
        
        img = img[np.newaxis, :]
        inputs = {onnx_model.get_inputs()[0].name: img}
         
        outs = onnx_model.run(None, inputs)
        result = process_op(outs[0])[0][0]
        return result
    def detpostpost(self,dt_boxes):
        if(len(dt_boxes))==0:
            return []
        dt_boxes=[db for db in dt_boxes]
        for i in range(len(dt_boxes)):
            dt_box=dt_boxes[i]
            if dt_boxes[i] is None:
                    continue
            for j in range(len(dt_boxes)):
                if j ==i:
                    continue
                if dt_boxes[j] is None:
                    continue
                m1,m2=min(dt_box[:,1]),max(dt_box[:,1])
                m3,m4=min(dt_boxes[j][:,1]),max(dt_boxes[j][:,1])
                if ((m1+m2)<m4*2 and (m1+m2)>m3*2) or((m3+m4)>m1*2 and (m3+m4)<m2*2):
                    y1=min(m1,m2)
                    y2=max(m3,m4)
                    x1=min(min(dt_box[:,0]),min(dt_boxes[j][:,0]))
                    x2=max(max(dt_box[:,0]),max(dt_boxes[j][:,0]))
                    dt_boxes[i]=np.array([[x1,y1],[x2,y1],[x2,y2],[x1,y2]])
                    dt_boxes[j]=None
            y1=min(dt_box[:,1])
            y2=max(dt_box[:,1])
            x1=min(dt_box[:,0])
            x2=max(dt_box[:,0])
            dt_boxes[i]=np.array([[x1,y1],[x2,y1],[x2,y2],[x1,y2]])
        dt_boxes=np.array([[dt[0][0],dt[0][1],dt[2][0],dt[2][1]] for dt in dt_boxes if dt is not None],dtype=np.int)
        return dt_boxes
    #@timer
    def ocr(self,img):
         
        t1=time.time()
        #box=mydetect(img)
        #if len(box)==0:
        try:
            
            box = self.get_boxes(img) 
            
            if len(box)==0:
                return ''
            if globalconfig['verticalocr']==False:
                box=self.detpostpost(box)
                
                
                index=np.argsort(box[:,1])
                box=box[index]
                t2=time.time()
                imgs=simplecrop(img,box)
            else:
                boxx=[]
                for b in box: 
                    boxx.append([np.min(b[:,0]),np.min(b[:,1]),np.max(b[:,0]),np.max(b[:,1])]) 
                index=np.argsort(-np.array(boxx)[:,1])
                 
                boxx=np.array(boxx,dtype=np.int)[index] 
                imgs=simplecrop(img,boxx)
                for i in range(len(imgs)):
                    imgs[i]=cv2.rotate(imgs[i],cv2.ROTATE_90_COUNTERCLOCKWISE)
                    
            res=self.recognition_img_croped(imgs)
            t3=time.time()
        #print(t3-t1,t3-t2,t2-t1)
        except:
            print_exc()
            return ''
        return  ''.join(res)
     

if __name__=='__main__':
    ocr=myocr() 
    print(ocr.ocr(cv2.imread('1.jpg')))