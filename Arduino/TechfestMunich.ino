#include <Wire.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Adafruit_LSM9DS1.h>
#include <Adafruit_SHT31.h>
#include <Adafruit_Sensor.h>
#include <ESP8266WiFiMulti.h>

const char* ssid     = "TECHFEST";
const char* password = "techfest19";
ESP8266WiFiMulti WiFiMulti;
const char* kServerAddress = "http://10.25.13.227:5000/measurement";
const int kMotionSensorPin = 12;
const int kSampleWindowMs = 100;
Adafruit_LSM9DS1* lsm;
Adafruit_SHT31* sht31;

void SetupWifi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(ssid, password);
  while ((WiFiMulti.run() != WL_CONNECTED)) {
    delay(250);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void SetupMotionSensor() {
  pinMode(kMotionSensorPin, INPUT);
  Serial.println("Motion sensor set up.");
}

void SetupAccGyroTemp() {
  lsm = new Adafruit_LSM9DS1();
  if (!lsm->begin()) {
    Serial.println("LSM9DS1 not found. Check your wiring!");
    while (1){ delay(100); }
  }
  Serial.println("LSM9DS1 found.");
  lsm->setupAccel(lsm->LSM9DS1_ACCELRANGE_2G);
  Serial.println("Accelerometer set up.");
  lsm->setupGyro(lsm->LSM9DS1_GYROSCALE_245DPS);
  Serial.println("Gyroscope set up.");
}

void SetupTempHumid() {
  sht31 = new Adafruit_SHT31();
  if (! sht31->begin(0x44)) {   // Set to 0x45 for alternate i2c addr
    Serial.println("SHT31 not found. Check your wiring!");
    while (1) { delay(100); }
  }
  Serial.println("SHT31 found.");
}

//void SetupHTTPClient() {
//  wifi_client = new WiFiClient();
//  http = new HTTPClient();
//  //http->setReuse(true);
//}

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("");
  Serial.println("Started.");
  SetupWifi();
  SetupMotionSensor();
  SetupAccGyroTemp();
  SetupTempHumid();
  // SetupHTTPClient();
}

void PutAmpIfNeeded(String *measurements_payload) {
  if(measurements_payload->length() > 0) {
    *measurements_payload += "&";
  }
}

void ReadAndPrintMotionSensor(String *measurements_payload) {
  int val = digitalRead(kMotionSensorPin);
  PutAmpIfNeeded(measurements_payload);
  *measurements_payload += "motion=";
  if (val == HIGH) {
    *measurements_payload += "true";
  } else {
    *measurements_payload += "false";
  }
  Serial.println(*measurements_payload);
}

void ReadAndPrintAccGyroTemp(String *measurements_payload) {
  sensors_event_t acc, gyro;
  lsm->getEvent(&acc, nullptr, &gyro, nullptr);
  PutAmpIfNeeded(measurements_payload);
  float acceleration = sqrt(acc.acceleration.x * acc.acceleration.x +
                            acc.acceleration.y * acc.acceleration.y +
                            acc.acceleration.z * acc.acceleration.z);
  float gyromotion = sqrt(gyro.gyro.x * gyro.gyro.x +
                          gyro.gyro.y * gyro.gyro.y +
                          gyro.gyro.z * gyro.gyro.z);
  *measurements_payload += "acceleration=" + String(acceleration) +
                           "&gyromotion=" + String(gyromotion);
  Serial.println(*measurements_payload);
}

void ReadAndPrintTempHumid(String *measurements_payload) {
  float temp = sht31->readTemperature();
  float humid = sht31->readHumidity();
  PutAmpIfNeeded(measurements_payload);
  *measurements_payload += "temperature=" + String(temp) +
                           "&humidity=" + String(humid);
  Serial.println(*measurements_payload);
}

void ReadAndPrintAudio(String* measurements_payload) {
  unsigned long start_time = millis();
  unsigned int peak_to_peak = 0;
 
  unsigned int signal_max = 0;
  unsigned int signal_min = 1024;
 
  while (millis() - start_time < kSampleWindowMs) {
    unsigned int sample = analogRead(0);
    if (sample > 1024) continue;
    if (sample > signal_max) {
      signal_max = sample;
    } else if (sample < signal_min) {
          signal_min = sample;
    }
  }
  peak_to_peak = signal_max - signal_min;
  double volts = (peak_to_peak * 3.3) / 1024;

  PutAmpIfNeeded(measurements_payload);
  *measurements_payload += "volume=" + String(volts);
  Serial.println(*measurements_payload);
}

void PostMeasurements(const String& measurements_payload) {
  WiFiClient wifi_client;
  HTTPClient http;
  http.setUserAgent("ESP8266!");
  if (!http.begin(wifi_client, kServerAddress)) {
    Serial.println("Could not establish HTTP connection.");
    delay(10000);
    return;
  }
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  http.addHeader("Accept", "*/*");
  int http_code = http.POST(measurements_payload);
  if(http_code != HTTP_CODE_OK) {
    Serial.printf("HTTP Error %d: %s\n", http_code,
                  http.errorToString(http_code).c_str());
    return;
  }
  
  String payload = http.getString();
  Serial.print("HTTP: "); Serial.println(payload);

  http.end();
}

void loop() {
  String measurements_payload;
  ReadAndPrintMotionSensor(&measurements_payload);
  ReadAndPrintAccGyroTemp(&measurements_payload);
  ReadAndPrintTempHumid(&measurements_payload);
  ReadAndPrintAudio(&measurements_payload);
  PostMeasurements(measurements_payload);
  delay(1000);
}
