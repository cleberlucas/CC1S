/*#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "S20+";
const char* password = "11111111"; 

ESP8266WebServer server(80);

#define botaoVermelho   3
#define botaoAzul   4
#define ledBotaoVermelho   5
#define ledBotaoAzul   6
#define ledReconheceuRosto   7
#define ledReconheceuQrcode   8

bool bloquearBotoes = false;
bool reconheceuRosto;

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

void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println('\n');

  pinMode(ledReconheceuRosto, OUTPUT);
  pinMode(ledReconheceuQrcode, OUTPUT);
  pinMode(ledBotaoAzul, OUTPUT);
  pinMode(ledBotaoVermelho, OUTPUT);

  digitalWrite(ledReconheceuRosto, HIGH);
  digitalWrite(ledReconheceuQrcode, HIGH);
  digitalWrite(ledBotaoAzul, HIGH);
  digitalWrite(ledBotaoVermelho, HIGH);

  delay(2000);

  digitalWrite(ledReconheceuRosto, LOW);
  digitalWrite(ledReconheceuQrcode, LOW);
  digitalWrite(ledBotaoAzul, LOW);
  digitalWrite(ledBotaoVermelho, LOW);

  //pinMode(botaoAzul, INPUT_PULLUP);
  //pinMode(botaoVermelho, INPUT_PULLUP);
  
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

#define LED_1   7
#define LED_2   8

void setup()
{
  // Configura pinos como saída
   Serial.begin(115200);
  delay(10);

  pinMode(LED_1, OUTPUT);
  pinMode(LED_2, OUTPUT);
}

void loop()
{
  // Pisca os LEDs de forma intercalada a cada 1 segundo
  digitalWrite(LED_1, HIGH);
  digitalWrite(LED_2, HIGH);

}

*/

#include <ESP8266WiFi.h>        // Include the Wi-Fi library

const char* ssid = "S20+";
const char* password = "11111111"; 

void setup() {
  Serial.begin(9600);         // Start the Serial communication to send messages to the computer
  delay(10);
  Serial.println('\n');
  
  WiFi.begin(ssid, password);             // Connect to the network
  Serial.print("Connecting to ");
  Serial.print(ssid); Serial.println(" ...");

  int i = 0;
  while (WiFi.status() != WL_CONNECTED) { // Wait for the Wi-Fi to connect
    delay(1000);
    Serial.print(++i); Serial.print(' ');
  }

  Serial.println('\n');
  Serial.println("Connection established!");  
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());         // Send the IP address of the ESP8266 to the computer
}

void loop() { }