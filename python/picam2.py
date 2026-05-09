import io
import time
from threading import Condition
from http import server
import socketserver
from picamera2.encoders import MJPEGEncoder
from picamera2 import Picamera2

# HTML 페이지 구성
PAGE = """\
<html>
<head><title>PiCamera2 MJPEG Streaming</title></head>
<body>
<h1>PiCamera2 MJPEG 스트리밍 데모</h1>
<img src="stream.mjpg" width="640" height="480"/>
</body>
</html>
"""

class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    
                    # 프레임 전송 (HTTP multipart 포맷)
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                print(f"클라이언트 접속 종료: {e}")
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# --- Picamera2 설정 및 실행 ---
picam2 = Picamera2()

# 1. 비디오 설정 생성 (MJPEG 포맷 직접 지정)
config = picam2.create_video_configuration(
    main={"format": "MJPEG", "size": (640, 480)}
)
picam2.configure(config)

output = StreamingOutput()

# 2. MJPEG 인코더를 생성하고 출력을 StreamingOutput으로 연결
# Picamera2는 start_recording 호출 시 인코더 객체를 전달받습니다.
encoder = MJPEGEncoder()
picam2.start_recording(encoder, output)

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    print("라즈베리 파이 카메라 서버가 8000번 포트에서 시작되었습니다.")
    server.serve_forever()
finally:
    # 3. 종료 시 리소스 해제
    picam2.stop_recording()
    picam2.close()
