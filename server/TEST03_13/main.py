from flask import Flask, Response, render_template
import boto3
import cv2

app = Flask(__name__)

# AWS Kinesis Video Stream 연결
client = boto3.client('kinesisvideo', region_name='ap-northeast-2')
stream_name = 'camera_rpi'

# Kinesis Video Stream에서 데이터를 수신하는 함수
def get_kinesis_video_stream():
    response = client.get_data_endpoint(
        StreamName=stream_name,
        APIName='GET_MEDIA'
    )
    data_endpoint = response['c2mc9ieuy0j15b.credentials.iot.ap-northeast-1.amazonaws.com']
    kvam = boto3.client('kinesis-video-media', endpoint_url=data_endpoint)
    response = kvam.get_media(
        StreamName=stream_name,
        StartSelector={'StartSelectorType': 'NOW'}
    )
    return response['Payload'].iter_chunks()

# Flask 루트 경로에 웹 페이지 렌더링
@app.route('/')
def index():
    return render_template('index.html')

# 웹 페이지에서 비디오 스트림 출력
@app.route('/video_feed')
def video_feed():
    def generate():
        # Kinesis Video Stream에서 데이터를 수신하고 디코딩하여 웹 페이지로 보냄
        for chunk in get_kinesis_video_stream():
            frame = cv2.imdecode(np.frombuffer(chunk, dtype=np.uint8), -1)
            ret, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
