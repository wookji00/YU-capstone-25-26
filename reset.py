# Picamera2 초기화 코드 
from picamera2 import Picamera2
# 전역 변수로 선언만 하고
picam2 = None 

def start_camera():
    global picam2
    picam2 = Picamera2()
    # 카메라가 시스템에서 이미 열려있다면 닫아줌
    picam2.close() 
    
    config = picam2.create_video_configuration(
        main={"size": (640, 480), "format": "BGR888"},
        transform=Transform(hflip=False, vflip=False)
    )
    picam2.configure(config)
    picam2.start()

# 실행부
if __name__ == "__main__":
    start_camera()  # 여기서 1회만 호출
    # ... 스레드 시작 및 app.run ...
