import os
import signal
import subprocess
import sys
import time

VENV_PYTHON = os.path.expanduser("~/projects/YU-capstone-25-26/python/.venv/bin/python")

SCRIPT1 = "gateway.py"
SCRIPT2 = "robotics_gateway.py"

BLUETOOTH_MAC = ""

processes = []

# 하위 프로세스를 전부 청소하는 함수
def terminate_all():
    print("프로세스 전부 종료")
    for p in processes:
        if p.poll is None:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGINT)
                print(f"프로세스 {p.pid}에 종료 신호 전송")
            except Exception as e:
                try:
                    p.terminate()
                    except Exeption:
                        pass
    print("모든 시스템 종료")

# main 함수 : 터미널 명령어를 순서대로 실행 및 프로세스로 할당
def main():
    if not os.path.exists(VENV_PYTHON):
        print(f"다음 파이썬 가상환경이 존재하지 않습니다 {VENV_PYTHON}")
        sys.exit(1)
    print("시스템 시작")
    try:
        rfcomm_cmd = ["sudo", "rfcomm", "connect", "0", BLUETOOTH_MAC]
        p_rfcomm = subprocess.Popen(
            rfcomm_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid
        )
        processes.append(p_rfcomm)
        time.sleep(3)
        robotics_cmd = [VENV_PYTHON, SCRIPT_ROBOTICS]
        p_robotics = subprocess.Popen(
            robotics_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid,
        )
        processes.append(p_robotics)
        time.sleep(1)

        gateway_cmd = [VENV_PYTHON, SCRIPT_GATEWAY]
        print(f"\n📡 [3/3] 블루투스-MQTT 게이트웨이 스크립트 실행 중... ({SCRIPT_GATEWAY})")

        p_gateway = subprocess.Popen(
            gateway_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid,
        )
        processes.append(p_gateway)

        while True:
            # rfcomm 프로세스가 조기 종료되었는지 검사 (연결 끊김 등)
            if p_rfcomm.poll() is not None:
                print("\n⚠️ [경고] 블루투스 연결(rfcomm) 프로세스가 다운되었습니다.")
                break

            if p_gateway.poll() is not None:
                print(f"\n⚠️ [경고] {SCRIPT_GATEWAY} 프로세스가 종료되었습니다.")
                break

            if p_robotics.poll() is not None:
                print(f"\n⚠️ [경고] {SCRIPT_ROBOTICS} 프로세스가 종료되었습니다.")
                break
            
            time.sleep(1)
        
    except KeyboardInterrupt:
        # 사용자가 Ctrl+C를 누르면 안전하게 진입
        pass
    except Exception as e:
        print(f"\n🔥 시스템 구동 중 치명적 에러 발생: {e}")
    finally:
        # 어떤 이유로든 루프를 빠져나오면 모든 하위 프로세스를 강제 청소
        terminate_all_processes()
