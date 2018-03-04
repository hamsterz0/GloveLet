#include <Mouse.h>

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
  
Adafruit_BNO055 bno = Adafruit_BNO055(55);
 
const int LONG_FLEX_PIN1=A0;
const int LONG_FLEX_PIN2=A1;
const int SHORT_FLEX_PIN=A2;

const float VCC=3.3;
float flex_routine(int FLEX_PIN,float R_DIV,float STRAIGHT_RESISTANCE,float BEND_RESISTANCE);
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(LONG_FLEX_PIN1,INPUT);
  pinMode(LONG_FLEX_PIN2,INPUT);
 pinMode(SHORT_FLEX_PIN,INPUT);
   if(!bno.begin())
  {
    
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  
  delay(1000);
    
  bno.setExtCrystalUse(true);
  
}

void loop() {
  // put your main code here, to run repeatedly:
  imu::Quaternion quat = bno.getQuat();
 imu:: Vector<3> lin_acc=bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);

 float LF1_bend=flex_routine(LONG_FLEX_PIN1,10000.0,12000.0,70000.0);
  float LF2_bend=flex_routine(LONG_FLEX_PIN2,10000.0,12000.0,70000.0);
  float SF_bend=flex_routine(SHORT_FLEX_PIN,10000.0,27000.0,150000.0);
  Serial.print("qW: ");
  Serial.print(quat.w(), 4);
  Serial.print(" qX: ");
  Serial.print(quat.y(), 4);
  Serial.print(" qY: ");
  Serial.print(quat.x(), 4);
  Serial.print(" qZ: "); 
  Serial.print(quat.z(), 4);
  //Serial.println("");
  Serial.println(lin_acc.x(),4);
 
  Serial.println(LF1_bend);
  Serial.println(LF2_bend);
  Serial.println(SF_bend);
}

float flex_routine(int FLEX_PIN,float R_DIV,float STRAIGHT_RESISTANCE,float BEND_RESISTANCE)
{
  int flexADC = analogRead(FLEX_PIN);
  float flexV = flexADC * VCC / 1023.0;
  float flexR = R_DIV * (VCC / flexV - 1.0);

  
  float angle = ((float)constrain(flexR,STRAIGHT_RESISTANCE, BEND_RESISTANCE)-STRAIGHT_RESISTANCE)/(BEND_RESISTANCE-STRAIGHT_RESISTANCE);

  
  return(angle);
  
}

