import socket
from flask import Flask, render_template, Response
import cv2
import numpy as np
import datetime
import os
import pyrebase
import json
import threading

app = Flask(__name__)

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
video_num = 3
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 코덱 설정
recording = False
cond = []
outputFrame = None

# YOLO 가중치 파일과 CFG 파일 로드
YOLO_net = cv2.dnn.readNet("yolov4.weights","yolov4.cfg")

YOLO_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
YOLO_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)


# YOLO NETWORK 재구성
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = YOLO_net.getLayerNames()
output_layers = [layer_names[i-1] for i in YOLO_net.getUnconnectedOutLayers()]

class VideoStreamingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global outputFrame
        global recording
        global cond

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
            YOLO_net.setInput(blob)
            outs = YOLO_net.forward(output_layers)

            class_ids = []
            confidences = []
            boxes = []

            for out in outs:

                for detection in out:

                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]

                    if confidence > 0.5:
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

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.45, 0.4)

            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    cond.append(label)
                    # score = confidences[i]

                    # 경계상자와 클래스 정보 이미지에 입력
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
                    cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5,
                                (255, 255, 255), 1)

            if len(cond) == 10 and not recording:
                now = datetime.datetime.now()
                nowDatetime_path = now.strftime('%Y-%m-%d %H_%M_%S')  # 파일이름으로는 :를 못쓰기 때문에 따로 만들어줌
                # 녹화 시작
                print("record start")
                recording = True
                filename = "웹캠 " + nowDatetime_path + ".mp4"
                output = cv2.VideoWriter(os.path.join(folderpath, filename), fourcc, 7,
                                         (frame.shape[1], frame.shape[0]))  # 파일명, 코덱, FPS, 해상도 설정

            elif len(cond) == 30 and recording:
                # 녹화 종료
                global video_num

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
                cond = []
                video_num += 1
                recording = False

            # 녹화 중이면, 프레임을 녹화 파일에 저장
            if recording:
                output.write(frame)

            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            outputFrame = frame


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def generate():
        global outputFrame
        # 현재 프레임을 전송
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + outputFrame + b'\r\n')


if __name__ == '__main__':
    # 멀티 쓰레딩 적용
    vs_thread = VideoStreamingThread()
    vs_thread.start()
    app.run(host='0.0.0.0', port=2204, threaded=True)