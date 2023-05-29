import time
import socket
from flask import Flask, render_template, Response
import cv2
import numpy as np
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

HOST = '10.0.7.147'
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

# YOLO 가중치 파일과 CFG 파일 로드
YOLO_net = cv2.dnn.readNet("5-3_best.weights","5-3_custom.cfg")

# YOLO_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
# YOLO_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# YOLO NETWORK 재구성
classes = []
with open("ClassNames.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = YOLO_net.getLayerNames()
output_layers = [layer_names[i[0]-1] for i in YOLO_net.getUnconnectedOutLayers()]

result_list = []

def object_detection(frame, result_list):

    h, w, c = frame.shape

    # YOLO 입력
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0),
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
            score = confidences[i]

            # 경계상자와 클래스 정보 이미지에 입력
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
            cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5,
                        (255, 255, 255), 1)

    ret, jpeg = cv2.imencode('.jpg', frame)
    frame = jpeg.tobytes()
    # 처리 결과를 리스트에 저장
    result_list.append(frame)




def start_video_stream():
    while True:
        # client에서 받은 stringData의 크기 (==(str(len(stringData))).encode().ljust(16))
        length = recvall(conn, 16)
        stringData = recvall(conn, int(length))
        data = np.fromstring(stringData, dtype='uint8')
        # data를 디코딩한다.
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)

        detection_thread = threading.Thread(target=object_detection, args=(frame, result_list))
        detection_thread.start()
        continue



def generate(result_list):
    # 멀티 쓰레딩 적용
    while True:
        if len(result_list) > 0:
            result = result_list.pop(0)
            # 현재 프레임을 전송
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + result + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    server_thread = threading.Thread(target=start_video_stream)
    server_thread.daemon = True
    server_thread.start()
    app.run(host='0.0.0.0', port=2204, threaded=True)