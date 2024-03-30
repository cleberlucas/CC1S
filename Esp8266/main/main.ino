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

#define botaoVermelho   D3
#define botaoAzul   D4
#define ledBotaoVermelho   D5
#define ledBotaoAzul   D6
#define ledReconheceuRosto   D7
#define ledReconheceuQrcode   D8

void handleReconheceuRosto() {
  digitalWrite(ledReconheceuRosto, HIGH);
}

void handleNaoReconheceuRosto() {
  digitalWrite(ledReconheceuRosto, LOW);
}

void handleReconheceuQrcode() {
  digitalWrite(ledReconheceuQrcode, HIGH);
}

void handleNaoReconheceuQrcode() {
  digitalWrite(ledReconheceuQrcode, LOW);
}

void handleLiberarBotoes() {
  pinMode(botaoAzul, INPUT);
  pinMode(botaoVermelho, INPUT);
}

void handleTravarBotoes() {
  pinMode(botaoAzul, INPUT_PULLUP);
  pinMode(botaoVermelho, INPUT_PULLUP);
}

void sendDataInitoServer() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    String payload = "{\"id\": 8266, \"url\": \"" + WiFi.localIP().toString() + "\", \"ssid\": \"" + ssid + "\"}";

    Serial.println("Enviando requisição para o servidor...");

    http.begin(client, String(dbApiClient) + "/enviar-url");
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(payload);

    if (httpCode > 0) {
      String response = http.getString();
      Serial.println("Resposta do servidor: " + response);
    } else {
      Serial.println("Erro ao enviar requisição para o servidor");
      Serial.println(http.errorToString(httpCode));
    }

    http.end();
  } else {
    Serial.println("Erro: não conectado à rede WiFi");
  }
}

void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println('\n');

  pinMode(ledReconheceuRosto, OUTPUT);
  pinMode(ledReconheceuQrcode, OUTPUT);
  pinMode(ledBotaoAzul, OUTPUT);
  pinMode(ledBotaoVermelho, OUTPUT);

  pinMode(botaoAzul, INPUT_PULLUP);
  pinMode(botaoVermelho, INPUT_PULLUP);
  
  WiFi.begin(ssid, password);
  Serial.print("Conectando a ");
  Serial.print(ssid); 
  Serial.println(" ...");

  int i = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(++i); 
    Serial.print(' ');
  }

  sendDataInitoServer();

  Serial.println('\n');
  Serial.println("Conexão estabelecida!");  
  Serial.print("Endereço IP:\t");
  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/plain", "Olá! Este é o servidor ESP8266.");
  });

  server.on("/reconheceu-rosto", HTTP_GET, handleReconheceuRosto);
  server.on("/nao-reconheceu-rosto", HTTP_GET, handleNaoReconheceuRosto);
  server.on("/reconheceu-qrcode", HTTP_GET, handleReconheceuQrcode);
  server.on("/nao-reconheceu-qrcode", HTTP_GET, handleNaoReconheceuQrcode);
  server.on("/liberar-botoes", HTTP_GET, handleLiberarBotoes);
  server.on("/travar-botoes", HTTP_GET, handleTravarBotoes);

  server.begin();
}

void loop() {
  server.handleClient();
}