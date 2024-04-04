#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>

//
// WARNING!!! PSRAM IC required for UXGA resolution and high JPEG quality
//            Ensure ESP32 Wrover Module or other board with PSRAM is selected
//            Partial images will be transmitted if image exceeds buffer size
//
//            You must select partition scheme from the board menu that has at least 3MB APP space.
//            Face Recognition is DISABLED for ESP32 and ESP32-S2, because it takes up from 15 
//            seconds to process single frame. Face Detection is ENABLED if PSRAM is enabled as well

// ===================
// Select camera model
// ===================
//#define CAMERA_MODEL_WROVER_KIT // Has PSRAM
//define CAMERA_MODEL_ESP_EYE // Has PSRAM
//#define CAMERA_MODEL_ESP32S3_EYE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_PSRAM // Has PSRAM
//#define CAMERA_MODEL_M5STACK_V2_PSRAM // M5Camera version B Has PSRAM
//#define CAMERA_MODEL_M5STACK_WIDE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_ESP32CAM // No PSRAM
//#define CAMERA_MODEL_M5STACK_UNITCAM // No PSRAM
#define CAMERA_MODEL_AI_THINKER // Has PSRAM
//#define CAMERA_MODEL_TTGO_T_JOURNAL // No PSRAM
//#define CAMERA_MODEL_XIAO_ESP32S3 // Has PSRAM
// ** Espressif Internal Boards **
//#define CAMERA_MODEL_ESP32_CAM_BOARD
//#define CAMERA_MODEL_ESP32S2_CAM_BOARD
//#define CAMERA_MODEL_ESP32S3_CAM_LCD
//#define CAMERA_MODEL_DFRobot_FireBeetle2_ESP32S3 // Has PSRAM
//#define CAMERA_MODEL_DFRobot_Romeo_ESP32S3 // Has PSRAM
#include "camera_pins.h"

WiFiClient client;
WebServer server(88);

// WiFi credentials
const char* ssid = "":
const char* password = "";

// Server Facial Data Access Layer URL
String serverURL = "";

// Logs
String logs = "";

// ID and Location
String deviceID = "";
String deviceLocal = "";

void startCameraServer();
void setupLedFlash(int pin);

void handleStartMe() {
  if (server.hasArg("url") && server.hasArg("id") && server.hasArg("local")) {
    serverURL = server.arg("url");
    deviceID = server.arg("id");
    deviceLocal = server.arg("local");

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      String payload = "{\"id\": " + deviceID + ", \"url\": \"" + WiFi.localIP().toString() + "\", \"ssid\": \"" + ssid + "\", \"local\": " + deviceLocal + "}";

      updateLog("Starting ...");

      http.begin(client, String(serverURL) + "/esp");
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
      input[type=text], input[type=submit] {\
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
      <label for='url'>Server URL:</label><br>\
      <input type='text' id='url' name='url' value='" + serverURL + "'><br><br>\
      <label for='id'>Device ID:</label><br>\
      <input type='text' id='id' name='id' value='" + deviceID + "'><br><br>\
      <label for='local'>Device Location:</label><br>\
      <input type='text' id='local' name='local' value='" + deviceLocal + "'><br><br>\
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

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_QVGA;
  //config.pixel_format = PIXFORMAT_JPEG; // for streaming
  config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 4;
  config.fb_count = 1;
  
  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if(config.pixel_format == PIXFORMAT_JPEG){
    if(psramFound()){
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      // Limit the frame size when PSRAM is not available
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    // Best option for face detection/recognition
    //config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1); // flip it back
    s->set_brightness(s, 1); // up the brightness just a bit
    s->set_saturation(s, -2); // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  if(config.pixel_format == PIXFORMAT_JPEG){
    s->set_framesize(s, FRAMESIZE_QVGA);
  }

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

#if defined(CAMERA_MODEL_ESP32S3_EYE)
  s->set_vflip(s, 1);
#endif

// Setup LED FLash if LED pin is defined in camera_pins.h
#if defined(LED_GPIO_NUM)
  setupLedFlash(LED_GPIO_NUM);
#endif

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
  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

  server.on("/configuration", HTTP_GET, handleConfiguration);

  server.on("/start-me", HTTP_POST, handleStartMe);

  server.begin();

  startCameraServer();
}

void loop() {
  server.handleClient();
}
