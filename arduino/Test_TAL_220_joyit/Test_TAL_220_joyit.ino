#include "HX711.h"
// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 4;
const int LOADCELL_SCK_PIN = 5;
const int Calibration_Weight = 200;
HX711 scale;
void setup() {
 Serial.begin(9600);
 scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
 scale.set_scale();
 delay(1000);
 scale.tare();

 
 Serial.println("Calibration");
 Serial.println("Put a known weight on the scale");
 delay(5000);
 float x = scale.get_units(10);
 x = x / Calibration_Weight;
 scale.set_scale(x);
 Serial.println(x);
 Serial.println("Calibration finished...");
 delay(5000);

 }
void loop() {
  if (Serial.available() > 0)
  {
    // look for a command
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.equalsIgnoreCase("RESET"))
    {
      Serial.println("Resetting the tare");
      scale.tare(20);
      Serial.println("Done");
    }
  }

 if (scale.is_ready()) {
 float reading = scale.get_units(10);
 Serial.print("Force: ");
 Serial.println(reading);
 } else {
 Serial.println("HX711 not found.");
 }
 delay(100);
}
