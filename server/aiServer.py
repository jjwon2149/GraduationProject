import socket
import cv2
import numpy as np
import datetime
import os
import pyrebase
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging


# socket에서 수신한 버퍼를 반환하는 함수
def recvall(sock, count):
    # 바이트 문자열
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


HOST = '172.31.24.231'
PORT = 8000

# TCP 사용
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# 서버의 아이피와 포트번호 지정
s.bind((HOST, PORT))
print('Socket bind complete')
# 클라이언트의 접속을 기다린다. (클라이언트 연결을 10개까지 받는다)
s.listen(1)
print('Socket now listening')

# 연결, conn에는 소켓 객체, addr은 소켓에 바인드 된 주소
conn, addr = s.accept()
print('addraccept')

# "apikey": "내 웹 키"
config = {
    "apiKey": "AIzaSyDemQe9Xq0glQDqqCrBI2MApQN6BgKkfzY",
    "authDomain": "avkit-with-tableview.firebaseapp.com",
    "databaseURL": "https://avkit-with-tableview-default-rtdb.firebaseio.com",
    "projectId": "avkit-with-tableview",
    "storageBucket": "avkit-with-tableview.appspot.com",
    "messagingSenderId": "37795166720",
    "appId": "1:37795166720:web:53d378fd709ce2ce7236e5",
    "measurementId": "G-XKW8F4TK14"
};

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

folderpath = "/home/ubuntu/replayVideo"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 코덱 설정

# 파이어베이스 노티피케이션
cred_path = "avkit-with-tableview-firebase-adminsdk-9cxss-868b35eff3.json"
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

registration_token = 'e0jveQtHH07FnguEDntQvA:APA91bFDjmYM4OmMiPaAyaSE92cEiqeOa7ySxZ50-UJoMjnPaDtHH8tvqy3iImk4nL1jyrzGA7eiE91ceW24gpVu30JOTMTqgoQnr_EAnPoySY0zSNxrxPMKlgBJF33UYmCBH1jn7dej'
message = messaging.Message(
    notification=messaging.Notification(
        title='Danger!',
        body='Please take action.'
    ),
    token=registration_token,
)

# YOLO 가중치 파일과 CFG 파일 로드 - person
YOLO_net_person = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")

YOLO_net_person.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
YOLO_net_person.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# YOLO 가중치 파일과 CFG 파일 로드 - action
YOLO_net_act = cv2.dnn.readNet("8-1.weights", "8-1.cfg")

YOLO_net_act.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
YOLO_net_act.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# YOLO NETWORK - person
classes_person = []
with open("coco.names", "r") as f:
    classes_person = [line.strip() for line in f.readlines()]
layer_names_person = YOLO_net_person.getLayerNames()
output_layers_person = [layer_names_person[i - 1] for i in YOLO_net_person.getUnconnectedOutLayers()]

# YOLO NETWORK - action
classes_act = []
with open("Final_class.names", "r") as f:
    classes_act = [line.strip() for line in f.readlines()]
layer_names_act = YOLO_net_act.getLayerNames()
output_layers_act = [layer_names_act[i - 1] for i in YOLO_net_act.getUnconnectedOutLayers()]

global outputFrame, limit, now, last_time


def person_detect(h, w, blob):
    global person_last_time
    YOLO_net_person.setInput(blob)
    outs_person = YOLO_net_person.forward(output_layers_person)

    class_ids = []
    confidences = []
    boxes = []
    center = []

    for out in outs_person:

        for detection in out:

            scores = detection[5:]
            class_id = np.argmax(scores)

            if class_id == 0:
                confidence = scores[class_id]
                if confidence > 0.7:
                    # Object detected
                    # detection은 scale된 좌상단, 우하단 좌표를 반환하는 것이 아니라, detection object의 중심좌표와 너비/높이를 반환
                    # 원본 이미지에 맞게 scale 적용 및 좌상단, 우하단 좌표 계산
                    center_x = int(detection[0] * w)
                    center_y = int(detection[1] * h)
                    dw = int(detection[2] * w)
                    dh = int(detection[3] * h)
                    # Rectangle coordinate
                    x = int(center_x - dw / 2)
                    y = int(center_y - dh / 2)
                    boxes.append([x, y, dw, dh])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.7, 0.4)

    if len(indexes) > 1:
        person_last_time = datetime.datetime.now()
        return True
    else:
        return False


recording = False
cond = 0
video_num = 1

while True:
    # client에서 받은 stringData의 크기 (==(str(len(stringData))).encode().ljust(16))
    length = recvall(conn, 16)
    stringData = recvall(conn, int(length))
    data = np.fromstring(stringData, dtype='uint8')

    # data를 디코딩한다.
    frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    # YOLO 입력
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (608, 608), (0, 0, 0),
                                 True, crop=False)
    if person_detect(h, w, blob):
        if not recording:
            YOLO_net_act.setInput(blob)
            outs_act = YOLO_net_act.forward(output_layers_act)

            class_ids = []
            confidences = []
            boxes = []

            for out in outs_act:

                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]

                    if confidence > 0.6:
                        # Object detected
                        center_x = int(detection[0] * w)
                        center_y = int(detection[1] * h)
                        dw = int(detection[2] * w)
                        dh = int(detection[3] * h)
                        # Rectangle coordinate
                        x = int(center_x - dw / 2)
                        y = int(center_y - dh / 2)
                        boxes.append([x, y, dw, dh])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.6, 0.4)

            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes_act[class_ids[i]])
                    print(label)

                    if cond == 0:
                        now = datetime.datetime.now()
                        limit = now + datetime.timedelta(seconds=15)
                    if label == "Falldown":
                        cond += 2
                    else:
                        cond += 1
                    # score = confidences[i]

                    # 경계상자와 클래스 정보 이미지에 입력
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
                    cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5,
                                (255, 255, 255), 1)

            # 파이어베이스 올리는 부분
            if cond >= 10:
                if datetime.datetime.now() < limit:
                    rec_start = datetime.datetime.now()
                    nowDatetime_path = rec_start.strftime('%Y-%m-%d %H_%M_%S')  # 파일이름으로는 : 를 못쓰기 때문에 따로 만들어줌

                    # 녹화 시작
                    print("record start")
                    response = messaging.send(message)
                    print('Successfully sent message:', response)
                    last_time = datetime.datetime.now()
                    recording = True
                    filename = "웹캠 " + nowDatetime_path + ".mp4"
                    output = cv2.VideoWriter(os.path.join(folderpath, filename), fourcc, 20,
                                             (frame.shape[1], frame.shape[0]))  # 파일명, 코덱, FPS, 해상도 설정
                else:
                    # output.release()
                    print("record cancled")
                    output = None
                    cond = 0
                    recording = False

        else:
            # 녹화 중이면, 프레임을 녹화 파일에 저장
            output.write(frame)
            tmp = datetime.datetime.now()
            if tmp - last_time > datetime.timedelta(seconds=15):
                # 녹화 종료
                print("record end")
                output.release()
                upload_file = folderpath + "/" + filename
                storage.child("폭력 감지된 비디오/" + filename).put(upload_file)
                fileUrl = storage.child("폭력 감지된 비디오/" + filename).get_url(1)  # 0은 저장소 위치, 1은 다운로드 url 경로이다.
                # 업로드한 파일과 다운로드 경로를 database에 저장하기. 그래야 나중에 사용할 수 있음. storage에서 검색은 안되기 때문임.

                # 데이터베이스에 파일 정보 저장
                db = firebase.database()
                d = {}
                d[filename] = fileUrl
                data = json.dumps(d)
                db.child("videos").child(video_num).update({"Title": nowDatetime_path})
                db.child("videos").child(video_num).update({"link": fileUrl})
                print("OK")

                output = None
                cond = 0
                video_num += 1
                recording = False

    else:
        if recording:
            output.write(frame)
            tmp = datetime.datetime.now()
            if tmp - person_last_time > datetime.timedelta(seconds=5):
                # 녹화 종료
                print("record end")
                output.release()
                upload_file = folderpath + "/" + filename
                storage.child("폭력 감지된 비디오/" + filename).put(upload_file)
                fileUrl = storage.child("폭력 감지된 비디오/" + filename).get_url(1)  # 0은 저장소 위치, 1은 다운로드 url 경로이다.
                # 업로드한 파일과 다운로드 경로를 database에 저장하기. 그래야 나중에 사용할 수 있음. storage에서 검색은 안되기 때문임.

                # 데이터베이스에 파일 정보 저장
                db = firebase.database()
                d = {}
                d[filename] = fileUrl
                data = json.dumps(d)
                db.child("videos").child(video_num).update({"Title": nowDatetime_path})
                db.child("videos").child(video_num).update({"link": fileUrl})
                print("OK")

                output = None
                cond = 0
                video_num += 1
                recording = False