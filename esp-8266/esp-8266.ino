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
#define button   D2
#define ledBlue   D1
#define ledRed   D6
#define ledGreen   D7

ulong userId;

enum SynchronizeStatus {
    SYNC_PENDING,
    SYNCHRONIZE,
    IGNORE
};

enum SynchronizeStatus synchronize = IGNORE;

// Door control coming soon

void handleLedYellowOn() {
  digitalWrite(ledYellow, HIGH);
  server.send(200, "text/plain", "LED Yellow turned on.");
}

void handleLedYellowOff() {
  digitalWrite(ledYellow, LOW);
  server.send(200, "text/plain", "LED Yellow turned off.");
}

void handleLedGreenOn() {
  digitalWrite(ledGreen, HIGH);
  server.send(200, "text/plain", "LED Green turned on.");
}

void handleLedGreenOff() {
  digitalWrite(ledGreen, LOW);
  server.send(200, "text/plain", "LED Green turned off.");
}

void handleLedRedOn() {
  digitalWrite(ledRed, HIGH);
  server.send(200, "text/plain", "LED Red turned on.");
}

void handleLedRedOff() {
  digitalWrite(ledRed, LOW);
  server.send(200, "text/plain", "LED Red turned off.");
}

void handleLedBlueOn() {
  digitalWrite(ledBlue, HIGH);
  server.send(200, "text/plain", "LED Blue turned on.");
}

void handleLedBlueOff() {
  digitalWrite(ledBlue, LOW);
  server.send(200, "text/plain", "LED Blue turned off.");
}

void handleOffLeds() {
  digitalWrite(ledYellow, LOW);
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, LOW);
  digitalWrite(ledBlue, LOW);
  server.send(200, "text/plain", "All LEDs turned off.");
}

void handleOnLeds() {
  digitalWrite(ledYellow, HIGH);
  digitalWrite(ledGreen, HIGH);
  digitalWrite(ledRed, HIGH);
  digitalWrite(ledBlue, HIGH);
  server.send(200, "text/plain", "All LEDs turned on.");
}

void handleUserGet() {
  String jsonResponse = "{\"user_id\":\"" + String(userId) + "\"}";
  server.send(200, "application/json", jsonResponse);
}

void handleUserPut() {
  if (server.hasArg("user_id")) {
    String newUserId = server.arg("user_id");
    userId = newUserId.toInt();
    server.send(200, "text/plain", "User ID updated to: " + newUserId);
  } else {
    server.send(400, "text/plain", "No user_id parameter provided.");
  }
}

void handleSynchronizePut() {
  synchronize = SYNCHRONIZE;
  server.send(200, "text/plain", "Synchronized.");
}

void handleSynchronizeGet() {
  String status;
  switch (synchronize) {
    case SYNC_PENDING:
      status = "SYNC_PENDING";
      break;
    case SYNCHRONIZE:
      status = "SYNCHRONIZE";
      break;
    case IGNORE:
      status = "IGNORE";
      break;
  }
  
  String jsonResponse = "{\"synchronize\":\"" + status + "\"}";
  server.send(200, "application/json", jsonResponse);
}

void handleSecurity() {
  if (digitalRead(D2) == 1 || synchronize == SYNCHRONIZE) {
    if (synchronize == IGNORE) { 
      synchronize = SYNC_PENDING;
      if (userId == 0) {
          digitalWrite(ledRed, HIGH);
      } else {
          digitalWrite(ledGreen, HIGH);
      }
    } else if (synchronize == SYNCHRONIZE) {
        if (userId == 0) {
          digitalWrite(ledRed, LOW);
        } else {
          digitalWrite(ledGreen, LOW);
          userId = 0;
        }
        synchronize = IGNORE;
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  pinMode(ledYellow, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  pinMode(ledRed, OUTPUT);
  pinMode(ledBlue, OUTPUT);

  pinMode(button, INPUT);

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

  server.on("/user", HTTP_GET, handleUserGet);
  server.on("/user", HTTP_PUT, handleUserPut);

  server.on("/synchronize", HTTP_GET, handleSynchronizeGet);
  server.on("/synchronize", HTTP_PUT, handleSynchronizePut);

  server.sendHeader("Access-Control-Allow-Origin", "*");

  server.begin();

  handleOffLeds();
}

void loop() {
  server.handleClient();
  handleSecurity();
}
