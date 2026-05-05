// 밴딩센서가 연결된 아날로그 핀 번호
const int flexPin = A0;

void setup() {
  // 시리얼 통신 시작
  Serial.begin(9600);
  Serial.println("--- Bending Sensor Test Start ---");
}

void loop() {
  // 1. 센서로부터 아날로그 값 읽기 (0 ~ 1023)
  int flexValue = analogRead(flexPin);

  // 2. 읽어온 값을 시리얼 모니터에 출력
  Serial.print("Sensor Value: ");
  Serial.print(flexValue);

  // 3. 값의 변화를 한눈에 보기 위해 간단한 그래프 형태 출력
  Serial.print("\tGraph: ");
  
  // 측정값 범위(400~800)는 실제 센서 굽힘 정도에 따라 수정이 필요할 수 있습니다.
  // 센서를 구부렸을 때와 폈을 때의 시리얼 모니터 수치를 보고 400, 800 숫자를 조절하세요.
  int visualValue = map(flexValue, 400, 800, 0, 50);
  visualValue = constrain(visualValue, 0, 50); // 그래프가 화면을 벗어나지 않게 제한

  for (int i = 0; i < visualValue; i++) {
    Serial.print("-");
  }
  Serial.println(">");

  // 4. 0.1초 대기
  delay(100);
}
