#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServer.h>

const char* ssid = "S20+";
const char* password = "11111111";
const char* dbApiClient = "http://192.168.21.192:5000";

WiFiClient client;
ESP8266WebServer server(80);

const int D0 = 16;
const int D1 = 5;
const int D2 = 4;
const int D3 = 0;
const int D4 = 2;
const int D5 = 14;
const int D6 = 12;
const int D7 = 13;
const int D8 = 15;

#define redButtonPin   D3
#define blueButtonPin   D4
#define redButtonLedPin   D5
#define blueButtonLedPin   D6
#define recognizedFaceLedPin   D7
#define recognizedQrCodeLedPin   D8

void handleRecognizedFace() {
  digitalWrite(recognizedFaceLedPin, HIGH);
}

void handleUnrecognizedFace() {
  digitalWrite(recognizedFaceLedPin, LOW);
}

void handleRecognizedQrCode() {
  digitalWrite(recognizedQrCodeLedPin, HIGH);
}

void handleUnrecognizedQrCode() {
  digitalWrite(recognizedQrCodeLedPin, LOW);
}

void handleEnableButtons() {
  pinMode(blueButtonPin, INPUT);
  pinMode(redButtonPin, INPUT);
}

void handleDisableButtons() {
  pinMode(blueButtonPin, INPUT_PULLUP);
  pinMode(redButtonPin, INPUT_PULLUP);
}

void sendDataToDbApiClient() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    String payload = "{\"id\": 8266, \"url\": \"" + WiFi.localIP().toString() + "\", \"ssid\": \"" + ssid + "\"}";

    Serial.println("Sending request to the server...");

    http.begin(client, String(dbApiClient) + "/esp/start");
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(payload);

    if (httpCode > 0) {
      String response = http.getString();
      Serial.println("Server response: " + response);
    } else {
      Serial.println("Error sending request to the server");
      Serial.println(http.errorToString(httpCode));
    }

    http.end();
  } else {
    Serial.println("Error: not connected to WiFi network");
  }
}

void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println('\n');

  pinMode(recognizedFaceLedPin, OUTPUT);
  pinMode(recognizedQrCodeLedPin, OUTPUT);
  pinMode(blueButtonLedPin, OUTPUT);
  pinMode(redButtonLedPin, OUTPUT);

  pinMode(blueButtonPin, INPUT_PULLUP);
  pinMode(redButtonPin, INPUT_PULLUP);
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to ");
  Serial.print(ssid); 
  Serial.println(" ...");

  int i = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(++i); 
    Serial.print(' ');
  }

  Serial.println('\n');
  Serial.println("Connection established!");  
  Serial.print("IP Address:\t");
  Serial.println(WiFi.localIP());

  sendDataToDbApiClient();

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/plain", "Hello! This is ESP8266 server.");
  });

  server.on("/recognized-face", HTTP_GET, handleRecognizedFace);
  server.on("/unrecognized-face", HTTP_GET, handleUnrecognizedFace);
  server.on("/recognized-qrcode", HTTP_GET, handleRecognizedQrCode);
  server.on("/unrecognized-qrcode", HTTP_GET, handleUnrecognizedQrCode);
  server.on("/enable-buttons", HTTP_GET, handleEnableButtons);
  server.on("/disable-buttons", HTTP_GET, handleDisableButtons);

  server.begin();
}

void loop() {
  server.handleClient();
}