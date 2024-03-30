#include <ESP8266WiFi.h>

char comando;
char comando_anterior;

const char COMANDO_RECONHECEU_ROSTO = 'A';
const char COMANDO_NAO_RECONHECEU_ROSTO = 'B';
const char COMANDO_RECONHECEU_QRCODE = 'C';
const char COMANDO_NAO_RECONHECEU_QRCODE = 'D';

const char* ssid = "NomeDaRedeWiFi";
const char* senha = "SenhaDaRedeWiFi";
const int portaServidor = 1234; // Porta que o ESP8266 escutará

WiFiServer servidor(portaServidor);

int ledReconheceuRosto;
int ledReconheceuQrcode;
int ledBotaoAzul;
int ledBotaoVermelho;

int botaoAzul;
int botaoVermelho;

void setup() {
  Serial.begin(9600);
  delay(100);

  conectarWiFi(ssid, senha);

  servidor.begin();

  ledReconheceuRosto = 1;
  ledReconheceuQrcode = 2;
  ledBotaoAzul = 4;
  ledBotaoVermelho = 5;

  pinMode(ledReconheceuRosto , OUTPUT);
  pinMode(ledReconheceuQrcode , OUTPUT);
  pinMode(ledBotaoAzul , OUTPUT);
  pinMode(ledBotaoVermelho , OUTPUT);

  botaoAzul = 6;
  botaoVermelho = 7;

  pinMode(botaoAzul , INPUT);
  pinMode(botaoVermelho , INPUT);
}

void loop() {
  if (Serial.available() > 0 || comando_anterior != comando) {
    WiFiClient cliente = servidor.available();
    if (cliente) {
      while (cliente.connected() && !cliente.available()) {
        delay(1);
      }
      comando = cliente.read();
    }
    if (Serial.available() > 0) {
      comando = Serial.read();
    }

    // Executar ações com base no comando recebido
    if (comando != comando_anterior) {
      switch (comando) {
        case COMANDO_RECONHECEU_ROSTO:
          // Faça algo quando reconhecer rosto
          digitalWrite(ledReconheceuRosto, HIGH);
          break;

        case COMANDO_NAO_RECONHECEU_ROSTO:
          // Faça algo quando não reconhecer rosto
          digitalWrite(ledReconheceuRosto, LOW);
          break;

        case COMANDO_RECONHECEU_QRCODE:
          // Faça algo quando reconhecer QR code
          digitalWrite(ledReconheceuQrcode, HIGH);
          break;

        case COMANDO_NAO_RECONHECEU_QRCODE:
          // Faça algo quando não reconhecer QR code
          digitalWrite(ledReconheceuQrcode, LOW);
          break;
      }

      comando_anterior = comando;
    }
  }
}

void conectarWiFi(const char* ssid, const char* senha) {
  Serial.print("Conectando à rede ");
  Serial.println(ssid);

  WiFi.begin(ssid, senha);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Conexão WiFi estabelecida");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());
}
