from flask import Flask, render_template, Response
import cv2
import numpy as np

app = Flask(__name__)
# 웹캠 신호 받기
VideoSignal = cv2.VideoCapture(-1)
# YOLO 가중치 파일과 CFG 파일 로드
YOLO_net = cv2.dnn.readNet("yolov4-tiny-custom_best.weights","yolov4-tiny-custom.cfg")

# YOLO NETWORK 재구성
classes = []
with open("ClassNames.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = YOLO_net.getLayerNames()
print(layer_names)
output_layers = [layer_names[i-1] for i in YOLO_net.getUnconnectedOutLayers()]
print(output_layers)
def gen():
    while True:
        # 웹캠 프레임
        ret, frame = VideoSignal.read()
#         frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
# 
#         # YOLO 입력
#         blob = cv2.dnn.blobFromImage(frame, 1, (608, 608), (0, 0, 0),
#                                      False, crop=True)
#         YOLO_net.setInput(blob)
#         outs = YOLO_net.forward(output_layers)

#         class_ids = []
#         confidences = []
#         boxes = []
# 
#         for out in outs:
# 
#             for detection in out:
# 
#                 scores = detection[5:]
#                 class_id = np.argmax(scores)
#                 confidence = scores[class_id]
# 
#                 if confidence > 0.5:
#                     # Object detected
#                     center_x = int(detection[0] * w)
#                     center_y = int(detection[1] * h)
#                     dw = int(detection[2] * w)
#                     dh = int(detection[3] * h)
#                     # Rectangle coordinate
#                     x = int(center_x - dw / 2)
#                     y = int(center_y - dh / 2)
#                     boxes.append([x, y, dw, dh])
#                     confidences.append(float(confidence))
#                     class_ids.append(class_id)
# 
#         indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.45, 0.4)
# 
#         for i in range(len(boxes)):
#             if i in indexes:
#                 x, y, w, h = boxes[i]
#                 label = str(classes[class_ids[i]])
#                 score = confidences[i]
# 
#                 # 경계상자와 클래스 정보 이미지에 입력
#                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
#                 cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5,
#                             (255, 255, 255), 1)
#                 print('tlkqjweflqnkw')
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def Piezo():
    GPIO.setmode(GPIO.BCM)
    gpio_pin = 12
    scale = [261, 587, 659, 349, 392, 440, 988, 523]
    GPIO.setup(gpio_pin, GPIO.OUT)
    list = [6, 2, 6, 2]
    try:
        p =GPIO.PWM(gpio_pin, 100)
        p.start(100)
        p.ChangeDutyCycle(90)
        
        for i in range(2):
            p.ChangeFrequency(scale[list[i]])
            time.sleep(0.05)
        p.stop()
    finally:
        GPIO.cleanup()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2204, threaded=True)