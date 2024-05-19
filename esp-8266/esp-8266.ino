#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServer.h>

WiFiClient client;
ESP8266WebServer server(88);

// **SET*** WiFi credentials
const char* ssid = ".";
const char* password = "........";

const int D0 = 16;
const int D1 = 5;
const int D2 = 4;
const int D3 = 0;
const int D4 = 2;
const int D5 = 14;
const int D6 = 12;
const int D7 = 13;
const int D8 = 15;

#define ledYellow   D0
#define ledRed   D6
#define ledGreen   D7
#define ledBlue   D8

void handleLedYellowOn() {
  digitalWrite(ledYellow, HIGH);
  sendResponse("LED Yellow turned on.");
}

void handleLedYellowOff() {
  digitalWrite(ledYellow, LOW);
  sendResponse("LED Yellow turned off.");
}

void handleLedGreenOn() {
  digitalWrite(ledGreen, HIGH);
  sendResponse("LED Green turned on.");
}

void handleLedGreenOff() {
  digitalWrite(ledGreen, LOW);
  sendResponse("LED Green turned off.");
}

void handleLedRedOn() {
  digitalWrite(ledRed, HIGH);
  sendResponse("LED Red turned on.");
}

void handleLedRedOff() {
  digitalWrite(ledRed, LOW);
  sendResponse("LED Red turned off.");
}

void handleLedBlueOn() {
  digitalWrite(ledBlue, HIGH);
  sendResponse("LED Blue turned on.");
}

void handleLedBlueOff() {
  digitalWrite(ledBlue, LOW);
  sendResponse("LED Blue turned off.");
}

void handleOffLeds() {
  digitalWrite(ledYellow, LOW);
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, LOW);
  digitalWrite(ledBlue, LOW);
  sendResponse("All LEDs turned off.");
}

void handleOnLeds() {
  digitalWrite(ledYellow, HIGH);
  digitalWrite(ledGreen, HIGH);
  digitalWrite(ledRed, HIGH);
  digitalWrite(ledBlue, HIGH);
  sendResponse("All LEDs turned on.");
}

void sendResponse(String message) {
  server.send(200, "text/plain", message);
}

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  pinMode(ledYellow, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  pinMode(ledRed, OUTPUT);
  pinMode(ledBlue, OUTPUT);

  handleOnLeds();

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
  Serial.print("Mac Address:\t");
  Serial.println(WiFi.macAddress());

  server.on("/led/yellow/on", HTTP_GET, handleLedYellowOn);
  server.on("/led/yellow/off", HTTP_GET, handleLedYellowOff);

  server.on("/led/green/on", HTTP_GET, handleLedGreenOn);
  server.on("/led/green/off", HTTP_GET, handleLedGreenOff);

  server.on("/led/red/on", HTTP_GET, handleLedRedOn);
  server.on("/led/red/off", HTTP_GET, handleLedRedOff);

  server.on("/led/blue/on", HTTP_GET, handleLedBlueOn);
  server.on("/led/blue/off", HTTP_GET, handleLedBlueOff);

  server.on("/leds/on", HTTP_GET, handleOnLeds);
  server.on("/leds/off", HTTP_GET, handleOffLeds);

  server.sendHeader("Access-Control-Allow-Origin", "*");

  server.begin();

  handleOffLeds();
}

void loop() {
  server.handleClient();
}