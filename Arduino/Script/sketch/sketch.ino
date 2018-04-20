#include <Mouse.h>

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
  
Adafruit_BNO055 bno = Adafruit_BNO055(55);
 
const int LONG_FLEX_PIN1=A0;
const int LONG_FLEX_PIN2=A1;
const int SHORT_FLEX_PIN1=A2;
const int SHORT_FLEX_PIN2=A3;

const float VCC=3.3;
float flex_routine(int FLEX_PIN,float R_DIV,float STRAIGHT_RESISTANCE,float BEND_RESISTANCE);
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LONG_FLEX_PIN1,INPUT);
  pinMode(LONG_FLEX_PIN2,INPUT);
  pinMode(SHORT_FLEX_PIN1,INPUT);
  pinMode(SHORT_FLEX_PIN2,INPUT);
   if(!bno.begin())
  {
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  
  delay(1000);
    
  bno.setExtCrystalUse(true);
  Serial.println("successful@");
}

void loop() {
  // put your main code here, to run repeatedly:
  imu::Quaternion quat = bno.getQuat();
  imu:: Vector<3> lin_acc=bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);

  float LF1_bend=flex_routine(LONG_FLEX_PIN1,10000.0,15000.0,40000.0);
  float LF2_bend=flex_routine(LONG_FLEX_PIN2,10000.0,20000.0,55000.0);
  float SF1_bend=flex_routine(SHORT_FLEX_PIN1,10000.0,30000.0,70000.0);
  float SF2_bend=flex_routine(SHORT_FLEX_PIN2,10000.0,50000.0,120000.0);

  Serial.print(lin_acc.x(),4);
  Serial.print(" ");
  Serial.print(lin_acc.y(),4);
  Serial.print(" ");
  Serial.print(lin_acc.z(),4);
  Serial.print(" ");
  Serial.print(quat.w(), 4);
  Serial.print(" ");
  Serial.print(quat.y(), 4);
  Serial.print(" ");
  Serial.print(quat.x(), 4);
  Serial.print(" ");
  Serial.print(quat.z(), 4);
  Serial.print(" ");
  Serial.print(LF1_bend);
  Serial.print(" ");
  Serial.print(LF2_bend);
  Serial.print(" ");
  Serial.print(SF1_bend);
  Serial.print(" ");
  Serial.println(SF2_bend);
}

float flex_routine(int FLEX_PIN,float R_DIV,float STRAIGHT_RESISTANCE,float BEND_RESISTANCE)
{
  int flexADC = analogRead(FLEX_PIN);
  float flexV = flexADC * VCC / 1023.0;
  float flexR = R_DIV * (VCC / flexV - 1.0);
  
  float angle = ((float)constrain(flexR,STRAIGHT_RESISTANCE, BEND_RESISTANCE)-STRAIGHT_RESISTANCE)/(BEND_RESISTANCE-STRAIGHT_RESISTANCE);
  
  return(angle);
  
}

