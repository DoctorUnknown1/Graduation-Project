import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt,QTimer,QAbstractTableModel,QThread,pyqtSignal,pyqtSlot,QObject,QDate,QPoint
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap,QImage,QColor
from PIL import Image
from DatabaseManager import DBManager
from My_Face_recognizer import FaceRecognizer
import numpy as np
import cv2,os
import time,random,shutil
from utils import *
from NeuralNet import MlTrainer

class LiveCaptureThread(QObject):
    #finished = pyqtSignal()
    image_signal = pyqtSignal(np.ndarray,np.ndarray,bool)
    def __init__(self,cap,recognizer):
        super().__init__()
        self.cap=cap
        self.run=True
        self.recognizer=recognizer
    @pyqtSlot()
    def do_work(self):
        while self.run:
            result=False
            _,img=self.cap.read()
            if _:
                raw_img=img.copy()
                h,w=img.shape[:2]
                x1,y1,x2,y2=int(w/2)-200,int(h/2)-200,int(w/2)+200,int(h/2)+200
                raw_img=raw_img[y1:y2,x1:x2]
                try:
                    result=self.recognizer.detect_for_capture(img) 
                    print(result)                   
                except:
                    pass
                self.image_signal.emit(img,raw_img,result)
        self.cap.release()
class VideoThread(QObject):
    #finished = pyqtSignal()
    image_signal = pyqtSignal(np.ndarray,str)
    def __init__(self,cap,recognizer):
        super().__init__()
        self.cap=cap
        self.run=True
        self.recognizer=recognizer
    @pyqtSlot()
    def do_work(self):
        while self.run:
            result=False
            _,img=self.cap.read()
            if _:
                img=cv2.resize(img,(600,400))
                try:
                    id_=self.recognizer.detect(img)                    
                except:
                    pass
                self.image_signal.emit(img,id_)
        self.cap.release()
class classifyThread(QObject):
    #finished = pyqtSignal()
    image_signal = pyqtSignal(bool,str)
    def __init__(self,agent):
        super().__init__()
        self.agent=agent
        self.run=True
    @pyqtSlot()
    def do_work(self):
        while self.run:
            result=False
            imgfilename=mainwindow.imglistclass[mainwindow.imgindex]
            aipredict=self.agent.test(imgfilename)
            actual_class=mainwindow.class_dict[imgfilename]
            print(aipredict,actual_class)
            time.sleep(.5)
            if aipredict==actual_class:
                result=True
            else:
                result=False
            self.image_signal.emit(result,aipredict)
        


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("loginpage.ui",self)
        self.setWindowIcon(QIcon("system/sysicon/ATS_logo.png"))
        self.setStyleSheet('MainWindow{border-image:url(system/sysicon/back.png) 0 0 0 0 stretch stretch;}')
        self.showMaximized()
        self.timer=QTimer()
        self.timer.start(1)
        self.timer.timeout.connect(self.mainloop)        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setXOffset(15)
        self.shadow.setYOffset(15)
        self.shadow.setColor(QColor(0, 0, 0))
        self.loginframe.setGraphicsEffect(self.shadow)
        self.StackedWidget.setCurrentIndex(0)
        self.btnlogin.clicked.connect(self.login)
        #self.btnlogout.clicked.connect(self.logout)
        #self.btnsetting.clicked.connect(self.setting)
        self.btnregistermenu_2.clicked.connect(self.openregpage)
        #self.btnregister.clicked.connect(self.register)
        #self.btndetection.clicked.connect(self.opendetection)
        self.btnsubmit.clicked.connect(self.do_registration)
        self.btnlivecapture.clicked.connect(self.capture)
        self.btngenerate.clicked.connect(self.generatepage)
        self.btnclassify.clicked.connect(self.classifypage)
        self.btnback1.clicked.connect(self.backfrom)
        self.btnback2.clicked.connect(self.backfrom)
        self.btnplastic.clicked.connect(self.plasticselected)
        self.btnpaper.clicked.connect(self.paperselected)
        self.btnmetal.clicked.connect(self.metalselected)
        self.btnother.clicked.connect(self.otherselected)
        self.btnlogout.clicked.connect(self.logout)
        self.btnbackfromregister.clicked.connect(self.backfromreg)
        self.btnstarttraining.clicked.connect(self.starttraining)
        self.lblclassifyimg.mousePressEvent=self.classifyimgclicked
        self.lblbinplastic.mousePressEvent=self.plastic_clicked
        self.lblbinpaper.mousePressEvent=self.paper_clicked
        self.lblbinmetal.mousePressEvent=self.metal_clicked
        self.lblbinother.mousePressEvent=self.other_clicked
        self.btnstartclassify.clicked.connect(self.start_classify)
        self.setAcceptDrops(True)
        self.recognizer=FaceRecognizer()
        self.dbmanager=DBManager()
        self.StackedWidget.setCurrentIndex(0)
        self.cleandataset()
        self.generateforclassify()
        self.trainframe.setVisible(False)
        self.trainer=MlTrainer()
        self.reset()
    def reset(self):
        self.addfacefile=None
        self.capturing=False
        self.videoplaying=False
        self.livedetecting=False
        self.camid=0
        self.capturedimg=None
        self.username='None'
        self.logintimer=0
        self.matchtimer=0
        self.classifyrun=False
        self.imgindex=0
        self.question='none'
        self.trainimgno=0
        self.lastdetect=None
        self.score=0
        self.total=0
    def backfromreg(self):
        self.StackedWidget.setCurrentIndex(0)
        self.reset()
    def plastic_clicked(self,event):
        self.lblbinmetal.setStyleSheet("QLabel {  }")
        self.lblbinpaper.setStyleSheet("QLabel {  }")
        self.lblbinother.setStyleSheet("QLabel {  }")
        if self.lastdetect is not None:
            if self.lastdetect=='plastic':
                self.lblclassifyimg.setStyleSheet("QLabel {  }")
                self.score+=1
                self.lblbinplastic.setStyleSheet("QLabel { border: 5px solid green; padding: 10px; }")
                self.imglistclass.remove(self.imglistclass[self.imgindex])
                self.update_classify()
            else:
                self.lblbinplastic.setStyleSheet("QLabel { border: 5px solid red; padding: 10px; }")
                self.score-=1
            
    def paper_clicked(self,event):
        self.lblbinmetal.setStyleSheet("QLabel {  }")
        self.lblbinplastic.setStyleSheet("QLabel {  }")
        self.lblbinother.setStyleSheet("QLabel {  }")
        if self.lastdetect is not None:
            self.lblclassifyimg.setStyleSheet("QLabel {  }")
            if self.lastdetect=='paper':
                self.score+=1
                self.lblbinpaper.setStyleSheet("QLabel { border: 5px solid green; padding: 10px; }")
                self.imglistclass.remove(self.imglistclass[self.imgindex])
                self.update_classify()
            else:
                self.lblbinpaper.setStyleSheet("QLabel { border: 5px solid red; padding: 10px; }")
                self.score-=1
    def metal_clicked(self,event):
        self.lblbinplastic.setStyleSheet("QLabel {  }")
        self.lblbinpaper.setStyleSheet("QLabel {  }")
        self.lblbinother.setStyleSheet("QLabel {  }")
        
        if self.lastdetect is not None:
            if self.lastdetect=='metal':
                self.lblclassifyimg.setStyleSheet("QLabel {  }")
                self.score+=1
                self.lblbinmetal.setStyleSheet("QLabel { border: 5px solid green; padding: 10px; }")
                self.imglistclass.remove(self.imglistclass[self.imgindex])
                self.update_classify()
            else:
                self.lblbinmetal.setStyleSheet("QLabel { border: 5px solid red; padding: 10px; }")
                self.score-=1
    def other_clicked(self,event):
        self.lblbinplastic.setStyleSheet("QLabel {  }")
        self.lblbinpaper.setStyleSheet("QLabel {  }")
        self.lblbinmetal.setStyleSheet("QLabel {  }")
        if self.lastdetect is not None:
            if self.lastdetect=='others':
                self.lblclassifyimg.setStyleSheet("QLabel {  }")
                self.score+=1
                self.lblbinother.setStyleSheet("QLabel { border: 5px solid green; padding: 10px; }")
                self.imglistclass.remove(self.imglistclass[self.imgindex])
                self.update_classify()
            else:
                self.lblbinother.setStyleSheet("QLabel { border: 5px solid red; padding: 10px; }")
                self.score-=1

    def classifyimgclicked(self,event):
        if len(self.imglistclass)>0:
            self.lblbinmetal.setStyleSheet("QLabel {  }")
            self.lblbinplastic.setStyleSheet("QLabel {  }")
            self.lblbinpaper.setStyleSheet("QLabel {  }")

            self.lastdetect=self.trainer.test(self.imglistclass[self.imgindex])
            print(len(self.imglistclass))
            self.lblclassifyimg.setStyleSheet("QLabel { border: 5px solid green; padding: 10px; }")
        else:
            self.showmsg('All images already classified')
    
    def starttraining(self):
        self.showmsg('Training initiated please wait untill training completed')
        self.trainer.train()
        self.showmsg('Training completed')
    def cleandataset(self):
        for folder in ['plastic','paper','metal','others']:
            path=f'dataset/train/{folder}'
            if os.path.exists(path):
                shutil.rmtree(path)
        for folder in ['plastic','paper','metal','others']:
            path=f'dataset/train/{folder}'
            os.mkdir(path)
    def saveimg(self,category):
        image=cv2.imread(self.imglist[self.imgindex])
        image=cv2.resize(image,(300,300))
        filename=f'dataset/train/{category}/{self.trainimgno}.png'
        cv2.imwrite(filename,image)
        self.trainimgno+=1
        self.imglist.pop(self.imgindex)
        self.generatepage()
    def plasticselected(self):
        self.saveimg('plastic')   
    def paperselected(self):
        self.saveimg('paper')
    def metalselected(self):
        self.saveimg('metal')
    def otherselected(self):
        self.saveimg('others')


    
    def backfrom(self):
        self.StackedWidget2.setCurrentIndex(0)
    def generatepage(self):
        self.StackedWidget2.setCurrentIndex(1)
        self.imglist,self.classdict=makeimagelist()
        self.getnximage()
    def getnximage(self):
        if len(self.imglist)>0:
            self.imgindex=random.randint(0,len(self.imglist))
            print(self.imgindex)
            image=cv2.imread(self.imglist[self.imgindex])
            image=cv2.resize(image,(300,300))
            pil_image = Image.fromarray(image)
            im2 = pil_image.convert("RGBA")
            data = im2.tobytes("raw", "RGBA")
            qim = QImage(data, pil_image.width, pil_image.height, QImage.Format_ARGB32)
            pixmap = QPixmap.fromImage(qim)
            self.lblgimage.setPixmap(pixmap)
            ##generate question
            self.question=f'What is this?'
            self.lblquestion.setText(self.question)
        else:
            self.showmsg('All images completed')
            self.stop_classify_thread()
    def generateforclassify(self):
        self.imglistclass,self.class_dict=makeimagelist()
    
    

    def getneximgclassify(self):
        if len(self.imglistclass)>1:
            self.imgindex=random.randint(0,len(self.imglistclass))
            imgfilename=self.imglistclass[self.imgindex]
            image=cv2.imread(imgfilename)
            image=cv2.resize(image,(300,300))
            pil_image = Image.fromarray(image)
            im2 = pil_image.convert("RGBA")
            data = im2.tobytes("raw", "RGBA")
            qim = QImage(data, pil_image.width, pil_image.height, QImage.Format_ARGB32)
            pixmap = QPixmap.fromImage(qim)
            self.lblclassifyimg.setPixmap(pixmap)
        else:
            self.showmsg('All images completed')

    def classifypage(self):
        self.StackedWidget2.setCurrentIndex(2)
    def update_result(self,result,prediction):
        self.total+=1
        if result:
            self.score+=1
        if prediction=='plastic':
            if result:
                self.lblbinplastic.setStyleSheet("border: 5px solid #32FF2C;")
            else:
                self.lblbinplastic.setStyleSheet("border: 5px solid red;")
            self.lblbinpaper.setStyleSheet("")
            self.lblbinmetal.setStyleSheet("")
            self.lblbinother.setStyleSheet("")
        if prediction=='paper':
            if result:
                self.lblbinpaper.setStyleSheet("border: 5px solid #32FF2C;")
            else:
                self.lblbinpaper.setStyleSheet("border: 5px solid red;")
            self.lblbinplastic.setStyleSheet("")
            self.lblbinmetal.setStyleSheet("")
            self.lblbinother.setStyleSheet("")
        if prediction=='metal':
            if result:
                self.lblbinmetal.setStyleSheet("border: 5px solid #32FF2C;")
            else:
                self.lblbinmetal.setStyleSheet("border: 5px solid red;")
            self.lblbinplastic.setStyleSheet("")
            self.lblbinpaper.setStyleSheet("")
            self.lblbinother.setStyleSheet("")
        if prediction=='others':
            if result:
                self.lblbinother.setStyleSheet("border: 5px solid #32FF2C;")
            else:
                self.lblbinother.setStyleSheet("border: 5px solid red;")
            self.lblbinplastic.setStyleSheet("")
            self.lblbinmetal.setStyleSheet("")
            self.lblbinpaper.setStyleSheet("")
        self.getneximgclassify()
        

    def start_classify(self):
        if self.classifyrun==False:
            self.generateforclassify()
            self.getneximgclassify()
            self.classify_thread = QThread()
            self.classify_worker = classifyThread(self.trainer)
            self.classify_worker.moveToThread(self.classify_thread)
            self.classify_thread.start()
            self.classify_thread.started.connect(self.classify_worker.do_work)
            self.classify_worker.image_signal.connect(self.update_result)
            self.classifyrun=True
            self.btnstartclassify.setText("Stop")
        elif self.classifyrun==True:
            self.stop_classify_thread()
            self.classifyrun=False
            self.btnstartclassify.setText("Start")
        
    def do_registration(self):
        name=self.leregname.text()
        if self.capturedimg is not None and name!='': 
            img=cv2.resize(self.raw_img,(200,200))
            cv2.imwrite(f'images/{name}.png',img)
            self.dbmanager.insert_into_admin(name,'1234')
            self.StackedWidget.setCurrentIndex(0)
            
        else:
            self.showmsg('Enter all field or capture image')


    def update_livedetect(self,image,id_):
        try:
            image=cv2.resize(image,(500,400))
            pil_image = Image.fromarray(image)
            im2 = pil_image.convert("RGBA")
            data = im2.tobytes("raw", "RGBA")
            qim = QImage(data, pil_image.width, pil_image.height, QImage.Format_ARGB32)
            pixmap = QPixmap.fromImage(qim)
            self.lblloginimg.setPixmap(pixmap)
            if id_!='Unknown':
                self.matchtimer+=1
                if self.matchtimer>30:
                    self.stop_video_playing_thread()
                    self.StackedWidget.setCurrentIndex(3)
                    self.StackedWidget2.setCurrentIndex(0)
                    self.username=id_
                    im=cv2.imread(f'images/{self.username}.png')
                    im=cv2.resize(im,(200,200))
                    pil_image = Image.fromarray(im)
                    im2 = pil_image.convert("RGBA")
                    data = im2.tobytes("raw", "RGBA")
                    qim = QImage(data, pil_image.width, pil_image.height, QImage.Format_ARGB32)
                    pixmap = QPixmap.fromImage(qim)
                    self.lbldp.setPixmap(pixmap)
                    self.lblprofilename.setText(self.username)
                    self.matchtimer=0
            else:
                self.logintimer+=1
                if self.logintimer>300:
                    self.stop_video_playing_thread()
                    self.StackedWidget.setCurrentIndex(0)
                    self.logintimer=0
                    self.showmsg('Login not success')



        except Exception as e:
            print(e)
        
             
   
    
        
                        
        
    def update_liveimgin(self,image,raw_img,result):
        self.raw_img=raw_img.copy()
        if result:
            self.btnlivecapture.setEnabled(True)
        else:
            self.btnlivecapture.setEnabled(False)
        try:
            pil_image = Image.fromarray(image)
            im2 = pil_image.convert("RGBA")
            data = im2.tobytes("raw", "RGBA")
            qim = QImage(data, pil_image.width, pil_image.height, QImage.Format_ARGB32)
            pixmap = QPixmap.fromImage(qim)
            self.lblregimg.setPixmap(pixmap)
        except Exception as e:
            print(e)
            #self.lblliveimgcapture.setText("No Camera Found")  

    def capture(self):
        self.entrycap=cv2.VideoCapture(self.camid)
        self.entrycap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        self.entrycap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        if self.capturing==False:
            try:
                self.capture_thread = QThread()
                self.capture_worker = LiveCaptureThread(self.entrycap,self.recognizer)
                self.capture_worker.moveToThread(self.capture_thread)
                self.capture_thread.start()
                self.capture_thread.started.connect(self.capture_worker.do_work)
                self.capture_worker.image_signal.connect(self.update_liveimgin)
                self.btnlivecapture.setText("CLICK NOW")
                self.capturing=True
            except:
                self.capturing=False
        elif self.capturing==True:
            self.capturedimg=self.raw_img.copy()
            self.btnlivecapture.setText("CAPTURE")
            self.stop_capture_thread()
            
    def stop_capture_thread(self):
        try:
            self.capture_worker.run=False
            self.capture_thread.terminate()
            self.btnlivecapture.setText("CAPTURE")
            self.btnlivecapture.setEnabled(True)
            self.capturing=False
            self.capturedimg=False
        except Exception as e:
            print(e)
        try:
            self.entrycap.release()
        except Exception as e:
            print(e)
    def stop_video_playing_thread(self):
        try:
            self.video_worker.run=False
            self.video_thread.terminate()
            self.videoplaying=False
            self.livedetecting=False
        except Exception as e:
            print(e)
        try:
            self.videocap.release()
        except Exception as e:
            print(e)
    def stop_classify_thread(self):
        try:
            self.classify_worker.run=False
            self.classify_thread.terminate()
        except Exception as e:
            print(e)
        
        

    

    def uploadface(self):
        filename=QFileDialog.getOpenFileName(self, 'upload a  photo')[0] 
        if filename:
            if filename[-4:].lower()==".jpg" or filename[-4:].lower()=="jpeg" or filename[-4:].lower()==".png":
                self.addfacefile=filename
                image=cv2.imread(self.addfacefile)
                image=cv2.resize(image,(600,700))
                image = QImage(image, image.shape[1],image.shape[0], image.shape[1] * 3,QImage.Format_RGB888).rgbSwapped()
                pix = QPixmap(image)
                self.lblregimg.setPixmap(pix)
        else:
            self.addfacefile=None
    def openregpage(self):
        self.StackedWidget.setCurrentIndex(2)
    def eyepressed(self):
        self.etpassword.setEchoMode(QLineEdit.Normal)
        self.btneye.setIcon(QIcon('system/sysicon/eyeicon.png'))
    def eyereleased(self):
        self.etpassword.setEchoMode(QLineEdit.Password) 
        self.btneye.setIcon(QIcon('system/sysicon/eyeicon_closed.png'))
    def showmsg(self,msg):
        msgBox=QMessageBox()
        msgBox.setText(msg)
        msgBox.exec()
    def login(self):
        self.StackedWidget.setCurrentIndex(1)
        if self.livedetecting==False:
            self.livedetecting=True
            self.videocap=cv2.VideoCapture(0)
            try:
                self.recognizer.thresold=0.45
                self.video_thread = QThread()
                self.video_worker = VideoThread(self.videocap,self.recognizer)
                self.video_worker.moveToThread(self.video_thread)
                self.video_thread.start()
                self.video_thread.started.connect(self.video_worker.do_work)
                self.video_worker.image_signal.connect(self.update_livedetect)
                self.livedetecting=True
            except:
                self.livedetecting=False
                    
        else:
            self.stop_video_playing_thread()
            self.livedetecting=False
        
    def logout(self):
        self.setStyleSheet('MainWindow{border-image:url(system/sysicon/back.png) 0 0 0 0 stretch stretch;}')
        self.StackedWidget.setCurrentIndex(0)
        self.reset()
    def mainloop(self):
        self.lblscore.setText(f'{self.score}/{self.total}')
        if self.trainimgno>5:
            self.trainframe.setVisible(True)
        else:
            self.trainframe.setVisible(False)
    
app=QApplication(sys.argv)
mainwindow=MainWindow()
mainwindow.show()
sys.exit(app.exec())