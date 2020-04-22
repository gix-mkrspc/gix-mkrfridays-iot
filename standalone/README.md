## Setup
first time:
`./install.sh && ./run.sh`
subsequently:
`./run.sh`

These scripts should be run from the same directory they exist in. After running `install.sh`, you only need to run `run.sh` in the future.

## Wiring Configuration
For the NodeMCU, please wire the servo to it as the following. The servo wire (yellow) should connect to D4, the ground to a GND pin, and power to a 3v3 pin.

![Servo](../assets/servo_bb.png)