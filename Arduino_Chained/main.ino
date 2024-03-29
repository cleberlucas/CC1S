int pino8 = 8;
int pino9 = 9;
int pino10 = 10;
int pino11 = 11;
int pino12 = 12;


void setup() {
  pinMode(pino8, OUTPUT);
  pinMode(pino9, OUTPUT);
  pinMode(pino10, OUTPUT);
  pinMode(pino11, OUTPUT);
  pinMode(pino12, OUTPUT);

  lightShow();
  
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char receivedChar = Serial.read();
    if (receivedChar == '0') {
          digitalWrite(pino8, LOW);
          digitalWrite(pino9, HIGH);
          digitalWrite(pino10, LOW);
          digitalWrite(pino11, LOW);
          digitalWrite(pino12, LOW);
          delay(100);
    }
    else if (receivedChar == '1')  {
          digitalWrite(pino8, LOW);
          digitalWrite(pino9, LOW);
          digitalWrite(pino10, LOW);
          digitalWrite(pino11, HIGH);
          digitalWrite(pino12, LOW);
          delay(100);
    }
  }
}

void lightShow() {
  digitalWrite(pino8, HIGH);
  digitalWrite(pino9, HIGH);
  digitalWrite(pino10, HIGH);
  digitalWrite(pino11, HIGH);
  digitalWrite(pino12, HIGH);

  delay(300);
  digitalWrite(pino8, LOW);
  digitalWrite(pino9, LOW);
  digitalWrite(pino10, LOW);
  digitalWrite(pino11, LOW);
  digitalWrite(pino12, LOW);

  delay(300);
  digitalWrite(pino8, HIGH);
  digitalWrite(pino9, HIGH);
  digitalWrite(pino10, HIGH);
  digitalWrite(pino11, HIGH);
  digitalWrite(pino12, HIGH);

  delay(300);
  digitalWrite(pino8, LOW);
  digitalWrite(pino9, LOW);
  digitalWrite(pino10, LOW);
  digitalWrite(pino11, LOW);
  digitalWrite(pino12, LOW);
}
