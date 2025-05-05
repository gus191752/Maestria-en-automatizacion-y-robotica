#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiUdp.h>
#include <NTPClient.h>

// ========= CONFIGURACIÓN ========= //
const char* ssid = "gus";               // Reemplaza con tu SSID
const char* password = "854317gamp";       // Reemplaza con tu contraseña
const char* scriptUrl = "https://script.google.com/macros/s/AKfycbySP2bX26APftvW72JPF-F7aWqDo7U7XFHBmqC8TAwlJKXofQvpqolpaP28Q1sRj6aL/exec"; // Tu URL de script

// Configuración NTP
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", -18000); // -5h GMT (ajusta según tu zona)

// ========= DECLARACIONES ========= //
#ifdef __cplusplus
extern "C" {
#endif
uint8_t temprature_sens_read(); // Para sensor interno ESP32
#ifdef __cplusplus
}
#endif

// ========= SETUP ========= //
void setup() {
  Serial.begin(115200);
  Serial.println("\nIniciando...");

  // Conexión WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 20) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConectado!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    
    // Iniciar NTP
    timeClient.begin();
    if(timeClient.update()) {
      Serial.println("Hora sincronizada: " + timeClient.getFormattedTime());
    }
  } else {
    Serial.println("\nError en conexión WiFi");
  }
}

// ========= LOOP ========= //
void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // Actualizar hora
    timeClient.update();
    String timestamp = timeClient.getFormattedTime();
    
    // Leer temperatura
    float tempC = (temprature_sens_read() - 32) / 1.8;
    Serial.print(timestamp);
    Serial.print(" - Temp: ");
    Serial.print(tempC);
    Serial.println(" °C");

    // Enviar a Google Sheets
    enviarDatos(timestamp, tempC);
  } else {
    Serial.println("Reconectando WiFi...");
    WiFi.reconnect();
  }
  
  delay(30000); // Espera 30 segundos
}

// ========= FUNCIONES ========= //

// Función para enviar datos (codificación URL incluida)
void enviarDatos(String timestamp, float temperatura) {
  HTTPClient http;
  
  // Codificar parámetros
  String url = String(scriptUrl) + 
              "?timestamp=" + urlEncode(timestamp) + 
              "&temp=" + String(temperatura);
  
  http.begin(url);
  int httpCode = http.GET();
  
  if (httpCode == HTTP_CODE_OK) {
    Serial.println("Datos enviados a Sheets!");
  } else {
    Serial.print("Error HTTP: ");
    Serial.println(httpCode);
    Serial.println("URL usada: " + url); // Para diagnóstico
  }
  http.end();
}

// Codificador URL para caracteres especiales
String urlEncode(String str) {
  String encoded = "";
  for (unsigned int i = 0; i < str.length(); i++) {
    char c = str.charAt(i);
    if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
      encoded += c;
    } else if (c == ' ') {
      encoded += "%20";
    } else if (c == ':') {
      encoded += "%3A";
    } else {
      encoded += "%" + String(c, HEX);
    }
  }
  return encoded;
}

