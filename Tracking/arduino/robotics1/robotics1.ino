#include <Servo.h>

Servo testServo;
int currentPin = -1;

void setup() {
  Serial.begin(9600);
  Serial.println("=== 서보 핀 테스트 ===");
  Serial.println("핀 번호 입력 후 엔터 (예: 3)");
  Serial.println("테스트 가능 핀: 3,5,6,9,10,11");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    int pin = input.toInt();

  if (currentPin != -1) {
    testServo.detach();
  }

  testServo.attach(pin);
  currentPin = pin;

  Serial.print("핀 D");
  Serial.print(pin);
  Serial.println(" 테스트 시작!");
  Serial.println("0도 -> 90도 -> 180도 순서로 움직입니다");

  testServo.write(0);delay(1000);
  testServo.write(90);delay(1000);
  testServo.write(180); delay(1000);
  testServo.write(90);delay(1000);

  Serial.println("완료! 움직였으면 이 핀 사용 가능 OK");
  Serial.println("다음 핀 번호 입력하세요");
  Serial.println("——————————————");
  }
}