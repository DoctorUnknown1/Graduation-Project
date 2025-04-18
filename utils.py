from datetime import datetime
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint
import os

def get_current_datetime():
    cdate=datetime.now().strftime("%d-%m-%Y")
    ctime=datetime.now().strftime("%H:%M:%S")
    cdtime=datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    return cdate,ctime,cdtime
def get_current_datetime_other_format():
    cdate=datetime.now().strftime("%Y-%m-%d")
    ctime=datetime.now().strftime("%H:%M:%S")
    return cdate,ctime


def copy(sourcefile,destfile):
    source_file =  open(sourcefile, 'rb')
    destination_file = open(destfile, 'wb')
    shutil.copyfileobj(source_file, destination_file)
def makeimagelist():
    image_list=[]
    class_dict={}
    folders=['plastic','paper','metal','others']
    for folder in folders:
        path=f'TOG/{folder}'
        files=os.listdir(path)
        for file in files:
            filepath=os.path.join(path,file)
            image_list.append(filepath)
            class_dict[filepath]=folder
    return image_list,class_dict
if __name__=="__main__":
    #print(send_mail("nazbul.ali@gmail.com"))
    #print(send_mail("preciousdjose@gmail.com"))
    pass

