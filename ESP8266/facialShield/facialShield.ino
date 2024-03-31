#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServer.h>

WiFiClient client;
ESP8266WebServer server(80);

const char* ssid = "S20+";
const char* password = "11111111";
const char* dbApiUrl = "http://192.168.21.192:5000";

const int D0 = 16;
const int D1 = 5;
const int D2 = 4;
const int D3 = 0;
const int D4 = 2;
const int D5 = 14;
const int D6 = 12;
const int D7 = 13;
const int D8 = 15;

#define ledWhite   D0
#define ledBlue   D5
#define ledYellow   D6
#define ledRed   D7
#define ledGreen   D8

void sendResponse() {
  server.send(200, "text/plain", "Request processed successfully.");
}

void handleDetectedFace() {
  digitalWrite(ledYellow, HIGH);
  sendResponse();
}

void handleUndetectedFace() {
  digitalWrite(ledYellow, LOW);
  sendResponse();
}

void handleRecognizedFace() {
  digitalWrite(ledGreen, HIGH);
  digitalWrite(ledRed, LOW);
  sendResponse();
}

void handleUnrecognizedFace() {
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, HIGH);
  sendResponse();
}

void handleRecognizedQr() {
  digitalWrite(ledGreen, HIGH);
  digitalWrite(ledRed, LOW);
  sendResponse();
}

void handleUnrecognizedQr() {
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, HIGH);
  sendResponse();
}

void handleDetectedQr() {
  digitalWrite(ledBlue, HIGH);
  sendResponse();
}

void handleUndetectedQr() {
  digitalWrite(ledBlue, LOW);
  sendResponse();
}

void handlerDoorOpen() {
  digitalWrite(ledWhite, HIGH);
  sendResponse();
}

void handlerDoorClose() {
  digitalWrite(ledWhite, LOW);
  sendResponse();
}

void handleOffLeds() {
  digitalWrite(ledWhite, LOW);
  digitalWrite(ledBlue, LOW);
  digitalWrite(ledYellow, LOW);
  digitalWrite(ledRed, LOW);
  digitalWrite(ledGreen, LOW);
  sendResponse();
}

void handleOnLeds() {
  digitalWrite(ledWhite, HIGH);
  digitalWrite(ledBlue, HIGH);
  digitalWrite(ledYellow, HIGH);
  digitalWrite(ledRed, HIGH);
  digitalWrite(ledGreen, HIGH);
  sendResponse();
}

void sendDataTodbApiUrl() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    String payload = "{\"id\": 8266, \"url\": \"" + WiFi.localIP().toString() + "\", \"ssid\": \"" + ssid + "\"}";

    Serial.println("Sending request to the server...");

    http.begin(client, String(dbApiUrl) + "/esp/start");
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

  pinMode(ledWhite, OUTPUT);
  pinMode(ledBlue, OUTPUT);
  pinMode(ledYellow, OUTPUT);
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);

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

  sendDataTodbApiUrl();

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/plain", "Hello! This is ESP8266 server.");
  });

  server.on("/face/detected", HTTP_GET, handleDetectedFace);
  server.on("/face/undetected", HTTP_GET, handleUndetectedFace);
  server.on("/face/recognized", HTTP_GET, handleRecognizedFace);
  server.on("/face/unrecognized", HTTP_GET, handleUnrecognizedFace);

  server.on("/qr/detected", HTTP_GET, handleDetectedQr);
  server.on("/qr/undetected", HTTP_GET, handleUndetectedQr);
  server.on("/qr/recognized", HTTP_GET, handleRecognizedQr);
  server.on("/qr/unrecognized", HTTP_GET, handleUnrecognizedQr);

  server.on("/door/open", HTTP_GET, handlerDoorOpen);
  server.on("/door/close", HTTP_GET, handlerDoorClose);

  server.on("/leds/off", HTTP_GET, handleOffLeds);
  server.on("/leds/on", HTTP_GET, handleOnLeds);

  server.begin();
}

void loop() {
  server.handleClient();
}