import time

from flask import Flask, render_template, Response
import cv2
import numpy as np
import threading
import datetime



app = Flask(__name__)
# 웹캠 신호 받기
VideoSignal = cv2.VideoCapture(0)
VideoSignal.set(3, 720)
VideoSignal.set(4, 1080)
# YOLO 가중치 파일과 CFG 파일 로드
YOLO_net = cv2.dnn.readNet("5-3_best.weights","5-3_custom.cfg")

# YOLO NETWORK 재구성
classes = []
with open("ClassNames.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = YOLO_net.getLayerNames()
output_layers = [layer_names[i-1] for i in YOLO_net.getUnconnectedOutLayers()]

#-- GPU 사용
# YOLO_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
# YOLO_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)


class VideoStreamingThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        cond = []
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 코덱 설정
        global recording
        recording = False
        global outputFrame
        # 동영상 캡처 및 프레임 생성 작업 수행
        while True:
            now = datetime.datetime.now()
            nowDatetime_path = now.strftime('%Y-%m-%d %H_%M_%S')  # 파일이름으로는 :를 못쓰기 때문에 따로 만들어줌
            # 프레임 생성
            # 웹캠 프레임
            ret, frame = VideoSignal.read()
            frame = cv2.flip(frame, 1)
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
                    cond.append(label)
                    # record(cond, frame)
                    score = confidences[i]

                    # 경계상자와 클래스 정보 이미지에 입력
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
                    cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5,
                                (255, 255, 255), 1)

            if len(cond) == 10 and not recording:
                # 녹화 시작
                print("record start")
                recording = True
                output = cv2.VideoWriter("웹캠 " + nowDatetime_path + ".avi", fourcc, 7,
                                (frame.shape[1], frame.shape[0])) # 파일명, 코덱, FPS, 해상도 설정
            elif len(cond) == 30 and recording:
                # 녹화 종료
                print("record end")
                recording = False
                output.release()
                output = None
                cond = []

            # 녹화 중이면, 프레임을 녹화 파일에 저장
            if recording:
                output.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

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
    while True:
        # 현재 프레임을 전송
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + outputFrame + b'\r\n')


if __name__ == '__main__':
    # 멀티 쓰레딩 적용
    vs_thread = VideoStreamingThread()
    vs_thread.start()
    app.run(host='0.0.0.0', port=2204, threaded=True)
