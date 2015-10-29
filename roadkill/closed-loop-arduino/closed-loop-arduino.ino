#include <Servo.h> 
 
#define SERVO_PIN 10

Servo myservo;  // create servo object to control a servo 
 
int potpin = 0;  // analog pin used to connect the potentiometer
int val;    // variable to read the value from the analog pin 
 
void setup() 
{ 
  myservo.attach(SERVO_PIN);  // attaches the servo on pin 9 to the servo object 
  Serial.begin(9600);
}
 
void loop() 
{ 
  val = analogRead(potpin);            // reads the value of the potentiometer (value between 0 and 1023) 
  Serial.printf("Potentiometer value: %d\n", val);

  myservo.write(300);                  // sets the servo position according to the scaled value 
  delay(15);                           // waits for the servo to get there 
} 

