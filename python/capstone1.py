# SPDX-FileCopyrightText: 2026 코딩 파트너 for User Project
# SPDX-License-Identifier: MIT

import os
import signal
import subprocess
import sys
import time

# [최종 지침 준수] 가상환경 내 파이썬 경로 및 가동 스크립트 매핑
VENV_PYTHON = os.path.expanduser("~/projects/YU-capstone-25-26/python/.venv/bin/python")

SCRIPT1 = "gateway.py"
SCRIPT2 = "robotics_gateway.py"

# 수정을 권장하는 매개변수: 실제 사용하는 블루투스 모듈 MAC 주소를 입력해 주세요.
BLUETOOTH_MAC = "98:DA:60:0C:F5:15"

processes = []

# 하위 프로세스를 전부 청소하는 함수
def terminate_all():
    print("\n🛑 [종료] 백그라운드 제어 프로세스 전체 일제 정리 시작...")
    for p in processes:
        if p.poll() is None:
            try:
                # 프로세스 그룹 전체에 신호를 전달하여 안전하게 정리합니다.
                os.killpg(os.getpgid(p.pid), signal.SIGINT)
                print(f"✅ 프로세스 {p.pid}에 종료 신호(SIGINT) 전송 완료")
            except Exception:
                try:
                    p.terminate()
                except Exception:
                    pass
    print("👋 모든 시스템 자원이 반납되었습니다. 종료합니다.")

# main 함수 : 터미널 명령어를 순서대로 실행 및 프로세스로 할당
def main():
    if not os.path.exists(VENV_PYTHON):
        print(f"❌ [오류] 다음 파이썬 가상환경이 존재하지 않습니다: {VENV_PYTHON}")
        sys.exit(1)
        
    print("🚀 [컨트롤러] 원격 로봇팔 시스템 통합 마스터 구동을 시작합니다.")
    
    try:
        # [1/3 단계] 블루투스 물리 드라이버 가동 (visudo 연동)
        # stdout과 stderr을 부모 터미널에 직접 연결하여 실시간 출력 차단 버그를 해결합니다.
        rfcomm_cmd = ["sudo", "rfcomm", "connect", "0", BLUETOOTH_MAC]
        print(f"\n📡 [1/3] 블루투스 연결 바인딩 시도 중... (명령: {' '.join(rfcomm_cmd)})")
        p_rfcomm = subprocess.Popen(
            rfcomm_cmd, stdout=sys.stdout, stderr=sys.stderr, preexec_fn=os.setsid
        )
        processes.append(p_rfcomm)
        time.sleep(3)
        
        # [2/3 단계] 로봇팔 제어 스크립트 실행
        robotics_cmd = [VENV_PYTHON, SCRIPT2]
        print(f"🤖 [2/3] 로봇팔 하드웨어 구독 및 서보 제어 노드 기동... ({SCRIPT2})")[cite: 8]
        p_robotics = subprocess.Popen(
            robotics_cmd, stdout=sys.stdout, stderr=sys.stderr, preexec_fn=os.setsid
        )
        processes.append(p_robotics)
        time.sleep(1)

        # [3/3 단계] 블루투스-MQTT 게이트웨이 스크립트 실행
        gateway_cmd = [VENV_PYTHON, SCRIPT1]
        print(f"📡 [3/3] 블루투스-MQTT 게이트웨이 파싱 발행 노드 기동... ({SCRIPT1})")[cite: 5]
        p_gateway = subprocess.Popen(
            gateway_cmd, stdout=sys.stdout, stderr=sys.stderr, preexec_fn=os.setsid
        )
        processes.append(p_gateway)

        print("\n✨ 모든 제어 파이프라인이 정상 기동되었습니다! 모니터링 가동 중... [종료: Ctrl+C]")
        print("=" * 70)

        # 실시간 상태 감시 루프 체계
        while True:
            if p_rfcomm.poll() is not None:
                print("\n⚠️ [경고] 블루투스 연결(rfcomm) 프로세스가 예기치 않게 다운되었습니다.")
                break

            if p_gateway.poll() is not None:
                print(f"\n⚠️ [경고] {SCRIPT1} 프로세스가 종료되었습니다.")[cite: 5]
                break

            if p_robotics.poll() is not None:
                print(f"\n⚠️ [경고] {SCRIPT2} 프로세스가 종료되었습니다.")[cite: 8]
                break
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 사용자의 강제 정지 명령(Ctrl+C)이 감지되었습니다.")
    except Exception as e:
        print(f"\n🔥 시스템 구동 중 치명적 에러 발생: {e}")
    finally:
        # 어떤 이유로든 루프를 빠져나오면 모든 하위 프로세스를 강제 청소
        terminate_all()

if __name__ == "__main__":
    main()
