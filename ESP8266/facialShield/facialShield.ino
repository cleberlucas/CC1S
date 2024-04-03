#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServer.h>

WiFiClient client;
ESP8266WebServer server(80);

// ===========================
// Enter your WiFi credentials
// ===========================
const char* ssid = "";
const char* password = "";

// ===========================
// Set server url facial-data-access-layer
// ===========================
const char* facialDataAccessLayerURL = "";

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
#define ledGreen   D6
#define ledRed   D7
#define ledBlue   D8

void sendResponse() {
  server.send(200, "text/plain", "Request processed successfully.");
}

void handleLedYellowOn() {
  digitalWrite(ledYellow, HIGH);
  sendResponse();
}

void handleLedYellowOff() {
  digitalWrite(ledYellow, LOW);
  sendResponse();
}

void handleLedGreenOn() {
  digitalWrite(ledGreen, HIGH);
  sendResponse();
}

void handleLedGreenOff() {
  digitalWrite(ledGreen, LOW);
  sendResponse();
}

void handleLedRedOn() {
  digitalWrite(ledRed, HIGH);
  sendResponse();
}

void handleLedRedOff() {
  digitalWrite(ledRed, LOW);
  sendResponse();
}

void handleLedBlueOn() {
  digitalWrite(ledBlue, HIGH);
  sendResponse();
}

void handleLedBlueOff() {
  digitalWrite(ledBlue, LOW);
  sendResponse();
}

void handleOffLeds() {
  digitalWrite(ledYellow, LOW);
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, LOW);
  digitalWrite(ledBlue, LOW);
  sendResponse();
}

void handleOnLeds() {
  digitalWrite(ledYellow, HIGH);
  digitalWrite(ledGreen, HIGH);
  digitalWrite(ledRed, HIGH);
  digitalWrite(ledBlue, HIGH);
  sendResponse();
}

void sendDataTofacialDataAccessLayerURL() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // ===========================
    // Change the id:8266 and local:1 if necessary
    // ===========================
    String payload = "{\"id\": 8266, \"url\": \"" + WiFi.localIP().toString() + "\", \"ssid\": \"" + ssid + "\", \"local\": 1}";

    Serial.println("Sending request to the server...");

    http.begin(client, String(facialDataAccessLayerURL) + "/esp");
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
    Serial.println("Not connected to WiFi network");
  }
}

void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println('\n');

  pinMode(ledYellow, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  pinMode(ledRed, OUTPUT);
  pinMode(ledBlue, OUTPUT);

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

  sendDataTofacialDataAccessLayerURL();

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/plain", "Hello! This is ESP8266 server.");
  });

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

  server.begin();
}

void loop() {
  server.handleClient();
}