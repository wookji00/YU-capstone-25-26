#include <SoftwareSerial.h>

const int pinBtn = 7;
bool stateBtn=false;
bool prevState=false;
bool toggleBtn=false;

// 핀 설정 및 소프트웨어 시리얼 선언
const int flexPin0 = A0;          // 검지손가락 밴딩 센서 (Analog 0)
const int flexPin1 = A1;          // 중지손가락 밴딩 센서 (Analog 0)
SoftwareSerial imuSerial(2, 3);   // IMU 센서 통신 (2: RX, 3: TX) -> 하드웨어 0,1번 핀 우회
SoftwareSerial btSerial(10, 11); // HC-06 블루투스 통신 (10: RX, 11: TX)

// WT901C485 Modbus 각도 요구 패킷
byte requestAngle[] = {0x50, 0x03, 0x00, 0x3D, 0x00, 0x03, 0x99, 0x86}; 
unsigned char rxBuffer[11];

void setup() {
  pinMode(pinBtn, INPUT_PULLUP); 
  Serial.begin(9600);    // PC 디버깅용 시리얼
  imuSerial.begin(9600);  // IMU 통신 속도
  btSerial.begin(9600);   // 블루투스 통신 속도

  Serial.println("WT901C485 Modbus + Checksum System Ready!");
  
  // 시작 시 블루투스 포트 활성화
  btSerial.listen();
}

void loop() {  
  stateBtn = (bool)digitalRead(pinBtn);

   if (stateBtn && stateBtn != prevState) { 
    // 모드 상태를 반전 (On ↔ Off)
    toggleBtn = !toggleBtn;
    Serial.println(toggleBtn);
    // 버튼을 계속 누르고 있어도 한 번만 인식하도록 대기
    delay(300); 
  }
  prevState=stateBtn;
  String dataString = "";
  if (toggleBtn){
    // 1. 검지손가락 구부림 센서 값 읽기 (로봇팔 집게 제어용)
    int flexValue0 = analogRead(flexPin0);
    int flexValue1 = analogRead(flexPin1);

    // 2. IMU 데이터 읽기 모드로 수신 포트 전환 및 명령 송신
    imuSerial.listen();
    imuSerial.write(requestAngle, 8);
    
    // 데이터 수신 대기 타임아웃 (최대 30ms로 대기 효율 최적화)
    unsigned long startTime = millis();
    int bufferIndex = 0;
    
    while (millis() - startTime < 30) {
      if (imuSerial.available()) {
        byte c = imuSerial.read();
        if (bufferIndex < 11) {
          rxBuffer[bufferIndex++] = c;
        } else {
          imuSerial.read(); // 버퍼 오버플로우 방지 및 찌꺼기 데이터 소거
        }
      }
    }

    // 3. 정상적인 Modbus 응답 패킷(11바이트) 검증 및 데이터 변환
    if (bufferIndex == 11 && rxBuffer[0] == 0x50 && rxBuffer[1] == 0x03) {
      // 2바이트 음수 표현을 위한 short 캐스팅 결합
      short rollRaw  = (rxBuffer[3] << 8) | rxBuffer[4];
      short pitchRaw = (rxBuffer[5] << 8) | rxBuffer[6];
      short yawRaw   = (rxBuffer[7] << 8) | rxBuffer[8];

      // 표준 각도 환산 공식 적용
      int roll  = int((long)rollRaw * 180 / 32768);
      int pitch = int((long)pitchRaw * 180 / 32768);
      int yaw   = int((long)yawRaw * 180 / 32768);
      
      // 4. 전송용 CSV 문자열 조립 (형식: "Roll,Pitch,Yaw,Flex,")
      dataString = String(roll) + "," + 
                          String(pitch) + "," + 
                          String(yaw) + "," + 
                          String(flexValue0) + "," +
                          String(flexValue1) + ",";
    } else {
      Serial.println("IMU Parsing Error or Packet Dropped");
      dataString = "0,0,0,230,270,";
    }
  } else {
    dataString = "0,0,0,230,270,";
  }
  // 5. 무선 통신 검증용 8비트 XOR 체크섬 계산
  byte checksum = 0;
  for (unsigned int i = 0; i < dataString.length(); i++) {
    checksum ^= dataString[i]; 
  }

  // 6. 라즈베리파이로 블루투스 패킷 최종 송신 
  // 최종 형태 예시: 12.34,-45.67,89.12,523,98\n
  btSerial.print(dataString);
  btSerial.println(checksum); // 맨 마지막에 체크섬 정수값과 줄바꿈 문자(\n)를 붙여 전송

  // PC 시리얼 모니터 확인용 출력
  Serial.print("Data: "); Serial.print(dataString);
  Serial.print(" | Checksum: "); Serial.println(checksum);

  delay(40);
  // 전체 루프 속도 조절 (라즈베리파이 로봇팔의 실시간 반응성을 위해 40ms로 단축)
}
