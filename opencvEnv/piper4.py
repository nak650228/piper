import cv2
import RPi.GPIO as GPIO
import time
import ast
import subprocess
from LedMatrix import display_message
from subprocess import PIPE
import os
       
# 超音波センサーから距離を取得
def checkdist():
    GPIO.output(16, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(16, GPIO.LOW)
    while not GPIO.input(18):
        pass
    t1 = time.time()
    while GPIO.input(18):
        pass
    t2 = time.time()
    return (t2-t1)*340/2

# PCF8591に接続されたフォトレジスタから光量を取得
def checkpr():
    proc = subprocess.run('i2cset -y 1 0x48 0x03; i2cget -y 1 0x48',shell=True,stdout=PIPE,text=True)

    # 取得した光量を16進から10進に変換
    pv = int(proc.stdout,16)
    return(pv) 

# MagicMirrorのNewsfeedを設定して、MagicMirrorを再起動する
def setNewsfeed(category):
    category_file="/home/piper/MagicMirror/config/config.js."+category
    com = 'cp '+category_file+' /home/piper/MagicMirror/config/config.js'
    proc = subprocess.run(com,shell=True,stdout=PIPE,text=True)
    proc = subprocess.run("pm2 restart mm",shell=True,stdout=PIPE,text=True)

#メインルーチン
if __name__ == '__main__':
    ESC_KEY = 27    
    INTERVAL= 33    
    FRAME_RATE = 30 


    DEVICE_ID = 0

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(16,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(18,GPIO.IN)

    # フォトレジスタの初期化
    proc = subprocess.run('i2cset -y 1 0x48 0x03; i2cget -y 1 0x48',shell=True,stdout=PIPE,text=True)

    # OpenCVの初期化 
    cascade_file = "../xml/haarcascade_frontalface_alt2.xml"
    cascade = cv2.CascadeClassifier(cascade_file)

    # Newsfeedの初期化
    setNewsfeed("top-picks")

    # パラメータの定義
    SLEEP_TIME = 1.0
    THRESHOLD_DISTANCE=1.0
    THRESHOLD_PHOTO=120
    THRESHOLD_COUNT = 15
    ID_FILE="/tmp/IDFile"
    count = 0

    # ユーザ認証結果ファイルが存在する場合、それを削除
    if os.path.exists(ID_FILE) :
        os.remove(ID_FILE)

    # is_identified　ユーザ認証済みを示すフラグ 
    is_identified = False


    while True:
        dist=checkdist()
        photov=checkpr()
        print ("Distance: ",str(dist),"Photo Val: ",photov)

        if dist < THRESHOLD_DISTANCE and photov > THRESHOLD_PHOTO and is_identified == False :
            # カメラから動画を取得し、そこから静止画を生成
            cap = cv2.VideoCapture(DEVICE_ID)
            while True :
                end_flag, c_frame = cap.read()
                if end_flag == True :
                    cap.release()
                    break

            # 静止画を白黒画像に変換し、そこに顔が映っているかを確認する
            img = c_frame
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_list = cascade.detectMultiScale(img_gray, minSize=(100, 100))

            count = 0

            # 顔が移っていた場合の処理（
            if len(face_list) == 1 :

                unixTime=int(time.time())
                fname = 'CapturedFace'+str(unixTime)+'.jpg'
                tmp_fname="/tmp/"+fname
                cv2.imwrite(tmp_fname,img_gray)
                
                # 撮影した画像をS3のバケットにコピーする
                proc = subprocess.run("aws s3 cp "+tmp_fname+" s3://piper-in/"+fname, shell=True )
                status = proc.stdout

                rfname=fname.replace(".jpg",".txt")
                result_fname=rfname.replace("CapturedFace","Result")

                display_message( [0x3C,0x42,0xA5,0x81,0x81,0x99,0x42,0x3C], 10)
                # AWS Recognition の解析結果ファイルをS3経由で受け取った後、これを削除
                proc = subprocess.run("aws s3 cp s3://piper-out/"+result_fname+" "+ID_FILE, shell=True )
                proc = subprocess.run("aws s3 rm s3://piper-out/"+result_fname, shell=True )

                fp = open(ID_FILE, 'r')
                result_data = fp.read()
                fp.close()

                print ("Result Data :",result_data)

                dic=ast.literal_eval(result_data)
                print("Name is :",dic['Name'])
                print("NewsFeed is :",dic['NewsFeed'])
                print("WorkPlace is :",dic['WorkPlace'])
                print("TrainInfo :",dic['TrainInfo'])
                is_identified = True
                setNewsfeed(dic['NewsFeed'])

        elif dist >= THRESHOLD_DISTANCE and is_identified == True:
            count += 1
            print ("Count:", count)
            if count > THRESHOLD_COUNT:
                count=0
                is_identified = False
                if os.path.exists(ID_FILE) :
                    os.remove(ID_FILE)
                setNewsfeed("top-picks")

        else:
            count=0

        time.sleep(SLEEP_TIME)
        


    cap.release()
    GPIO.cleanup()
