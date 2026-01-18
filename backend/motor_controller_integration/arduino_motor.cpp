// --- ARDUINO SKETCH ---
const int IN1 = 8;
const int IN2 = 9;
const int IN3 = 10;
const int IN4 = 11;

// 8-step sequence (Half-stepping for smoothness)
const int stepSequence[8][4] = {
  {1,0,0,0}, {1,1,0,0}, {0,1,0,0}, {0,1,1,0},
  {0,0,1,0}, {0,0,1,1}, {0,0,0,1}, {1,0,0,1}
};

int currentStep = 0;

void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  
  // Start Serial at 9600 baud
  Serial.begin(9600);
  
  // Flash LED to show reset
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  // Check if data is available in the Serial buffer
  if (Serial.available() > 0) {
    
    // Read the command until newline character
    // Format expected: "F,200" or "B,500"
    char direction = Serial.read(); // Read first char ('F' or 'B')
    Serial.read();                  // Read and discard the comma
    int steps = Serial.parseInt();  // Read the integer
    
    // Clear any remaining characters (like newline)
    while(Serial.available()) Serial.read();

    if (steps > 0) {
       // Execute the move
       moveBatch(direction, steps);
       
       // Send confirmation back to Pi
       Serial.print("DONE: Moved ");
       Serial.print(direction);
       Serial.println(steps);
    }
  }
}

void moveBatch(char dir, int steps) {
  bool forward = (dir == 'F' || dir == 'f');
  
  for (int i = 0; i < steps; i++) {
    stepMotor(forward);
    delay(2); // Speed control (Lower = Faster)
  }
  stopMotor();
}

void stepMotor(bool forward) {
  if (forward) {
    currentStep++;
    if (currentStep > 7) currentStep = 0;
  } else {
    currentStep--;
    if (currentStep < 0) currentStep = 7;
  }
  setPins(currentStep);
}

void setPins(int stepIndex) {
  digitalWrite(IN1, stepSequence[stepIndex][0]);
  digitalWrite(IN2, stepSequence[stepIndex][1]);
  digitalWrite(IN3, stepSequence[stepIndex][2]);
  digitalWrite(IN4, stepSequence[stepIndex][3]);
}

void stopMotor() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}