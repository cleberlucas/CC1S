#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServer.h>

WiFiClient client;
ESP8266WebServer server(88);

// **SET*** WiFi credentials
const char* ssid = "PIRAMIDE 2.4Ghz";
const char* password = "cleiton388";

String logs = "";

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

void handleStartMe() {
  if (server.hasArg("url") && server.hasArg("id") && server.hasArg("local")) {
    String url = server.arg("url");
    String id = server.arg("id");
    String local = server.arg("local");

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      String payload = "{\"id\": " + id + ", \"url\": \"" + WiFi.localIP().toString() + "\", \"ssid\": \"" + ssid + "\", \"local\": " + local + ", \"mac\": \"" + WiFi.macAddress() + "\"}";

      updateLog("Starting ...");

      http.begin(client, String(url) + "/esp");
      http.addHeader("Content-Type", "application/json");

      int httpCode = http.POST(payload);

      if (httpCode > 0) {
        String response = http.getString();
        updateLog("Server response: " + response);
      } else {
        updateLog("Error sending request to the server");
        updateLog(http.errorToString(httpCode));
      }

      http.end();
    } else {
      updateLog("Not connected to WiFi network");
    }
  } else {
    updateLog("Missing parameters in the request.");
  }

  sendLogs();
}

void handleConfiguration() {
  String htmlResponse = "<!DOCTYPE html>\
  <html>\
  <head>\
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\
    <style>\
      body { font-family: Arial, Helvetica, sans-serif; }\
      input[type=text], input[type=submit], select {\
        width: 100%;\
        padding: 12px;\
        border: 1px solid #ccc;\
        border-radius: 4px;\
        box-sizing: border-box;\
        margin-top: 6px;\
        margin-bottom: 16px;\
      }\
      input[type=submit] {\
        background-color: #4CAF50;\
        color: white;\
        padding: 14px 20px;\
        border: none;\
        border-radius: 4px;\
        cursor: pointer;\
      }\
      input[type=submit]:hover {\
        background-color: #45a049;\
      }\
      #logs {\
        padding: 10px;\
        border: 1px solid #ccc;\
        border-radius: 4px;\
        background-color: #f2f2f2;\
      }\
    </style>\
  </head>\
  <body>\
    <form action='/start-me' id='configForm' method='POST'>\
      <label for='url'>Data Access Server URL:</label><br>\
      <input type='text' id='url' name='url' value=''><br><br>\
      <label for='id'>Device ID:</label><br>\
      <input type='text' id='id' name='id' value=''><br><br>\
      <label for='local'>Device Location:</label><br>\
      <input type='text' id='local' name='local' value=''><br><br>\
      <input type='submit' value='Submit'>\
    </form>\
    <div id='logs'>" + logs + "</div>\
    <script>\
      function updateLogs() {\
        var logsDiv = document.getElementById('logs');\
        logsDiv.innerHTML = '" + logs + "';\
      }\
      setInterval(updateLogs, 1000);\
    </script>\
  </body>\
  </html>";

  server.send(200, "text/html", htmlResponse);
}

void sendResponse(String message) {
  server.send(200, "text/plain", message);
  updateLog(message);
}

void sendLogs() {
  server.send(200, "text/plain", logs);
}

void updateLog(String log){
    logs += log + "<br>";
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

  server.on("/configuration", HTTP_GET, handleConfiguration);

  server.on("/start-me", HTTP_POST, handleStartMe);

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

  while (Serial.available()) {
    char c = Serial.read();
    updateLog(String(c));
      sendLogs();
  }
}