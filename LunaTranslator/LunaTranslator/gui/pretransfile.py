from PyQt5.QtWidgets import QWidget,QLabel,QComboBox ,QPushButton,QFormLayout,QHBoxLayout,QDialogButtonBox,QDialog,QLineEdit,QMessageBox,QFileDialog

from PyQt5.QtCore import Qt,QSize 
import sqlite3
import json
from traceback import print_exc
import os
from myutils.config import globalconfig,_TR
from myutils.utils import autosql
from gui.usefulwidget import getQMessageBox
def sqlite2json(self):
    f=QFileDialog.getOpenFileName(directory='./translation_record', filter="*.sqlite")
    if f[0]=='' :
        return
    
    try:
        sql=autosql(sqlite3.connect(f[0],check_same_thread=False))
        ret=sql.execute('SELECT * FROM artificialtrans  ').fetchall()
        js={}
        js_format2={}
        collect={} 
        for _aret  in ret:
            if len(_aret)==4: 
                    
                _id,source,mt,ut=_aret
                js[source]={'userTrans':ut,'machineTrans':mt}
                js_format2[source]=mt
            elif len(_aret)==3: 
                _id,source,mt =_aret
                js[source]={'userTrans':'','machineTrans':''}
                js_format2[source]=''
            mtjs=json.loads(mt)
            for _i,_t in enumerate(mtjs):
                if  _i==0  :
                    js[source]['machineTrans']=mtjs[_t]
                    js_format2[source]=mtjs[_t]
                js[source]['result_'+str(_i)]=mtjs[_t]
                js[source]['api_'+str(_i)]=_t

                collect[_t]='result_'+str(_i)
            
    except:
        print_exc()
        getQMessageBox(self,"错误","所选文件格式错误！")
        return 

    dialog = QDialog(self,Qt.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle(_TR("导出翻译记录为json文件"))
    dialog.resize(QSize(800,10))
    formLayout = QFormLayout(dialog)  # 配置layout
    dialog.setLayout(formLayout)

    combo=QComboBox()
    combo.addItems([globalconfig['fanyi'][_]['name'] for _ in collect ])


    formLayout.addRow(_TR("首选翻译"),combo) 


    e=QLineEdit(f[0][:-(len('.sqlite'))])
        
    bu=QPushButton(_TR('选择路径')  )
    def __selectsavepath():
        ff=QFileDialog.getSaveFileName(dialog,directory=f[0][:-(len('.sqlite'))])
        if ff[0]=='' :
            return
        e.setText(ff[0])
    bu.clicked.connect(__selectsavepath)
    hori=QHBoxLayout()
    hori.addWidget(e)
    hori.addWidget(bu)
    formLayout.addRow(_TR("保存路径"),hori) 

    button = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel) 
    formLayout.addRow(button)
    button.rejected.connect(dialog.close)
    
    def __savefunction():
        if len(collect.keys())>0:
            transkirokuuse=list(collect.keys())[combo.currentIndex()]
            for k in js:
                if collect[transkirokuuse] in js[k]:
                    js[k]['machineTrans']=js[k][collect[transkirokuuse]]  
                    
        with open(e.text()+'.complex.json','w',encoding='utf8') as ff:
            ff.write(json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
        with open(e.text()+'.simple.json','w',encoding='utf8') as ff:
            ff.write(json.dumps(js_format2,ensure_ascii=False,sort_keys=False, indent=4))
        dialog.close()
    button.accepted.connect(__savefunction)
    button.button(QDialogButtonBox.Ok).setText(_TR('确定'))
    button.button(QDialogButtonBox.Cancel).setText(_TR('取消'))
    dialog.show()
