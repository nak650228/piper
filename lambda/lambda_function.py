# coding: UTF-8
import json
import urllib.parse
import boto3
import time
from datetime import datetime, timedelta, timezone
#from chalice import Chalice

REGION = "ap-northeast-1"
REKOGNITION = boto3.client('rekognition')
AWS_S3_BUCKET_NAME = "piper-out"
JST = timezone(timedelta(hours=+9), 'JST')


def lambda_handler(event, context):
    #S3にデータがアップロードされたのをトリガーにしてバケット名とファイル名を取得

    s3 = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
 
    sns = boto3.client('sns')
    TOPIC_ARN = 'Replace Your ARN here'
    

    dynamodb = boto3.resource('dynamodb')
    table    = dynamodb.Table('Users')
    logtable = dynamodb.Table('LoginInfo')
    
    result = table.scan()
    items = result['Items']
    return_value={ "Name":"none",
                   "NewsFeed":"top-picks",
                   "WorkPlace":"none",
                   "TrainInfo":"none"
    }
 
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        #画像処理をかけてレスポンスを受け取る

        for userData in items:
            print("Now processing",userData["Name"])
            return_faces = detect_faces(bucket,key,userData["ImageName"])
            print(return_faces)
            
            face_matches=return_faces["FaceMatches"]
            print ("face_matches:",face_matches)
            if (face_matches) :
                return_value={ "Name":userData["Name"], 
                               "NewsFeed":userData["NewFeed"], 
                               "WorkPlace":userData["WorkPlace"] , 
                               "TrainInfo":userData["TrainInfo"]
                }
                print(return_value)
                
                analyze_face=REKOGNITION.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':key}},Attributes=['ALL'])
                print(analyze_face)
                for faceDetail in analyze_face['FaceDetails']:
                    genderInfo = str(faceDetail['Gender'])
                    is_smile = str(faceDetail['Smile'])
                    emotionInfo = str(faceDetail['Emotions'][0]["Type"])
                    print("Gender: "+ genderInfo)
                    print("Smile: " + is_smile)
                    print("Emotions: " + emotionInfo)
                
                # ログイン履歴に追加
                dt_now = datetime.now(JST)
                time_now = str(dt_now.time())
                date_now = str(dt_now.date())
                SeqNo=int(time.time())   
                
                logtable.put_item(Item={ "SequenceNo": SeqNo, "UserName": userData["Name"], "Date": date_now, "Time": time_now, "Emotion": emotionInfo })
            
                # SNSでログインしたことを通知
                if userData["IsConfirm"] :
                    msg = '[ ' + date_now + ' ' + time_now + ' ] : User ' + userData["Name"] + ' logged in Mirror (' + emotionInfo + ')'
                    subject = 'Login information'
                
                    response = sns.publish(
                        TopicArn = TOPIC_ARN,
                        Message = msg,
                        Subject = subject
                    )

        #認証結果ファイル書き出し用のs3オブジェクトを作る
        newfilename = str(key).replace(".jpg", ".txt")
        logfilename = newfilename.replace("CapturedFace","Result")
        #認証結果ファイルの名前をlog_(ファイル名)_(拡張子)_YYYY-MM-DD-HH-MM-SS.txtにして書き出し
        #logfilename = 'log_' + newfilename + "_" + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.txt'
        object = boto3.resource('s3').Object(AWS_S3_BUCKET_NAME, logfilename)

        data = str(return_value)
        

        #ファイルの書き出し
        object.put(Body=data)

        return return_faces

        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e



#顔認識
def detect_faces(b,i,jpeg):
    try:
        print("Backet Name:",b,"Source image:",i,"User Image:",jpeg)
        response = REKOGNITION.compare_faces(
            SourceImage={'S3Object':{'Bucket':b,'Name':i}},
            TargetImage={'S3Object':{'Bucket':"piper-family-data",'Name':jpeg}},
            SimilarityThreshold=80
        )
        
        return response
    except Exception as ex:
        return 0

