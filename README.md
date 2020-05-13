# GIX IoT
## Components
- NodeMCU Wifi development board *1
- Servo motor (with three types of arm) *1
- Enclosure box (MDF sheet) *6
- Waving sign *1
---
## Hardware Setup
1. Assemble the box
> In progress
2. Plug servo to NodeMCU ( Yellow-D4, Red-3.3v, Brown-GND )

![Servo Breadboard](./assets/servo_bb.png)
![Servo Real](./assets/servo_real.png)

---
## Software Setup
*Prerequisites*
- working wifi, you know the SSID(name) & password
- computer or phone

We've already flashed the basic programm, all you need to do is follow the bellow steps and connect it to your wifi.

The process will be...
- Connct to NodeMCU wifi
- Tell it your own wifi name and password
- Let it connect to your wifi
- Connect back to your own wifi
- use your own wifi to control it

### Detail Steps
1. Plug in the micro USB cable (just for providing power, don't need to connect to a computer)
2. Use your device (PC/phone) and connect to wifi name: "gix_iot"
3. Password: "gixmkrspc"
4. wait for the webpage to popup, you will see this
![ap_screenshot](./assets/ap_screenshot.png)
(If the page didn't show up after you connceted to the wifi, try go to http://192.168.4.1/)
5. Enter your **own wifi's** SSID(name) & password,
 you can use your home wifi, phone hotspot, etc.
6. Wait a few seconds after you see the seccess message. Press RST button on the NodeMCU and let the NodeMCU connect to your wifi
7. Disconnect your device from "gix_iot" and reconnect your device to your own wifi
8. Open your browser and go to [http://servo_test.local](http://servo_test.local) you will see this page
![control_screenshot](./assets/control_screenshot.png)
> If you can't see this page, try refresh the page several times in 1-2 minutes. After 1-2 minutes, if you still can't see this page. Go back to step **2.** and connect to "gix_iot" again. This time you might get a wifi list in your popup page, connect to the wifi you want.
9. Click Toggle, you can move the servo now! 👏👏👏
> If the wifi setting is setup successfully, NodeMCU will automaticlly connect to your wifi everytime it boots up.

> If your want to connect to another wifi, turn off the or get away from the setuped wifi signal. Once it fail to connect to wifi it will start "ap mode" and you can reset it from step **2.**