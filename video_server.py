import cv2
import time
import threading
import json
from datetime import datetime
from flask import Flask, Response, render_template
from picamera2 import Picamera2
from libcamera import Transform
from PIL import ImageFile

fps_value = 0.0
# 데이터가 일부 잘려도 에러를 내지 않고 로드하도록 설정
ImageFile.LOAD_TRUNCATED_IMAGES = True

app = Flask(__name__)

# 1 Picam2를 전역으로 한번 초기화
picam2 = Picamera2()
print(Picamera2.global_camera_info())
video_config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "BGR888"}, transform=Transform(hflip=False, vflip=False)
)
picam2.configure(video_config)
picam2.start()

# 2 최신프레임 저장할 전역 변수 락 생성
global_frame = None
frame_lock = threading.Lock()


def capture_frames():
    """백그라운드 스레드에서 지속적으로 프레임을 캡처하여 global_frame 갱신"""
    global global_frame, fps_value
    frame_count = 0
    last_time = time.time()
    while True:
        # picam2 로부터 프레임 캡처 (numpy array)
        frame_data = picam2.capture_array()

        # 필요하면 OpenCV 처리
        frame_data = cv2.cvtColor(frame_data, cv2.COLOR_RGB2BGR)
        
        # FPS count
        frame_count += 1
        current_time = time.time()
        if current_time - last_time >= 1.0:
            fps_value = frame_count / (current_time - last_time)
            frame_count = 0
            last_time = current_time
            
            # ? ?? ?? ?? ??
            # 'fps_log.txt' ??? ??? ?? FPS? ???? ?????.
            try:
                with open("fps_log.txt", "a") as f:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{now_str}] FPS: {fps_value:.2f}\n")
            except Exception as e:
                print(f"?? ?? ??: {e}")

        # 프레임 을 JPEG 로 인코딩
        ret, buffer = cv2.imencode(".jpg", frame_data)
        if not ret:
            continue
        frame = buffer.tobytes()

        # 스레드 안전하게 전역 변수 업데이트
        with frame_lock:
            global_frame = frame

        # 너무 빠른 루프로 인한 과부하를 방지하기 위해 짧게 대기
        time.sleep(0.01)


# 3 백그라운드 스레드 시작
capture_thread = threading.Thread(target=capture_frames)
capture_thread.daemon = True
capture_thread.start()


def gen_frames():
    """각 클라이어느의 요청마다 호출되어 global_frame 을 스트리밍"""
    while True:
        with frame_lock:
            frame = global_frame
        if frame is None:
            continue
        yield (b"--frame\r\nContent-Type: image/ jpeg\r\n\r\n" + frame + b"\r\n")
        time.sleep(0.01)


@app.route("/")
def index():
    # 클라이언트에서 영상 스트리밍을 확인할 HTML 템플릿 렌더링
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    # 여러 클라이언트가 접근해도 동일한 global_frame을 읽어 스트리밍
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

# fps 요청
@app.route("/get_fps")
def get_fps(): # 현재 fps rate를 요청 할때 보내줌
    return json.dumps({"fps": round(fps_value, 2)})

# 서버가 모든 네트워크 인터페이스에서 접근 가능하게 하기
if __name__ == "__main__":
    try:
        app.run(
            host="0.0.0.0", port=5000, debug=False, use_reloader=False
        )  # 기본적으로 디버그 모드에서는 코드변경을 감지해서 서버를 자동 재시작하는 리로더가 초기화됨.
        # 이 기능이 초기화 코드를 2번 실행하게 할수도 있으므로 비활성화
    finally:
        picam2.stop()



# mkdir -p template 후 index.html 만들기
