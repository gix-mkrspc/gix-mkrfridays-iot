<!-- Place this tag in your head or just before your close body tag. -->
<script async defer src="https://buttons.github.io/buttons.js"></script>
<div style="text-align:center">
    <!-- star -->
    <a class="github-button" href="https://github.com/codycodes/gix-mkrfridays-iot/" data-icon="octicon-star" data-color-scheme="no-preference: light; light: light; dark: light;" data-size="large" aria-label="Star codycodes/gix-mkrfridays-iot on GitHub">Star</a>
    <!-- download -->
    <a class="github-button" href="https://github.com/codycodes/gix-mkrfridays-iot/archive/master.zip" data-icon="octicon-cloud-download" data-size="large" aria-label="Download codycodes/gix-mkrfridays-iot on GitHub">Download</a>
    <!-- issue -->
    <a class="github-button" href="https://github.com/codycodes/gix-mkrfridays-iot/issues" data-color-scheme="no-preference: light; light: light; dark: light;" data-size="large" aria-label="Issue codycodes/gix-mkrfridays-iot on GitHub">Issue</a>
</div>

## About
The NodeMCU is an open-source firmware and development kit which allows us to use a low-cost ESP8266 WiFi MCU to provide “the best platform for IOT application development at the lowest cost” [NodeMCU homepage](https://www.nodemcu.com/index_en.html).  

ESPHome is the software and firmware flasher we’ll be using; it’s a “system to control your ESP8266/ESP32 by simple yet powerful configuration files and control them remotely through Home Automation systems” [ESPHome homepage](https://esphome.io).

# Local Control (via ESPHome)

## Upon Completion
By completing this project you will have a device which can wave 👋 when its virtual button is pressed via its website.

## Components
- NodeMCU WiFi development board *1
- Servo motor (with three types of arm) *1
- Enclosure box (MDF sheet) *6
- Waving sign *1
  
---
## Hardware Setup
1. Assemble the box
> In progress
2. Plug servo to NodeMCU ( Yellow-D4, Red-3.3v, Brown-GND )
<div style="text-align:center">
<!-- make the following images centered -->
<img src="./assets/servo_bb.png" height="400">
<img src="./assets/servo_real.png" height="400">
</div>

---
## Software Setup
*Prerequisites*
- working WiFi, you know the SSID(name) & password
- computer or phone

We've already flashed the basic program, all you need to do is follow the below steps and connect it to your WiFi.

### The Overall Process
1. Connect to NodeMCU WiFi
2. Tell it your own WiFi name and password
3. Let it connect to your WiFi
4. Connect your phone back to your own WiFi
5. Use your own WiFi to browse to the device's web server to control it

### Detailed Steps
1. Plug in the micro USB cable (just for providing power, don't need to connect to a computer)
2. Use your device (PC/phone) and connect to the WiFi netowrk: "gix_iot"
3. Password: "gixmkrspc"
4. Wait for the webpage to popup, you will see this:
![ap_screenshot](./assets/ap_screenshot.png)
> (If the page didn't show up after you connected to the WiFi, try to go to http://192.168.4.1/)
>
> An iPhone or Android device may change the WiFi network back to your home network, since the NodeMCU doesn't have an Internet connection. You may need to ensure that "Auto Join" is turned off for your other WiFi (iPhone) or forget the other network (Android); this step is only to get the NodeMCU onto your home network and then you can re-join and/or turn on "Auto Join" for your home WiFi again.
5. Enter your **own WiFi's** SSID(name) & password,
 you can use your home WiFi, phone hotspot, etc.
6. Wait a few seconds after you see the success message. Press RST button on the NodeMCU and let the NodeMCU connect to your WiFi
7. Disconnect your device from "gix_iot" and reconnect your device to your own WiFi
8. Open your browser and go to [http://servo_test.local](http://servo_test.local) you will see this page:
![control_screenshot](./assets/control_screenshot.png)
> If you can't see this page, try refreshing the page several times in 1-2 minutes. After 1-2 minutes, if you still can't see this page. Go back to step **2.** and connect to "gix_iot" again. This time you might get a WiFi list in your popup page, connect to the WiFi you want.

9. Click Toggle, you can move the servo now 👋!
  
### Congratulations! 👏👏👏
Now that the WiFi connection is configured, your NodeMCU will automatically connect to your WiFi every time it boots up.

> If you want to connect to another WiFi, turn off or get away from the WiFi signal you previously connected to. Once the NodeMCU failed to connect to WiFi, it will start "ap mode" and you can reset it from step **2.**

> In the future we will have other activities involving this device! Please see the section below, tinker and bring any ideas or changes up so we can bring that functionality to other cohort members!

## Extensibility
As the microcontroller is easily reprogrammable, the hand wave can be triggered, or its action changed by possibilities only limited by your imagination! For instance, you can easily hook ESPHome into an automation platform called Home Assistant, which will allow you to wave the hand for all sorts of triggers; for instance, if someone opens your door, you can use the ESPHome to wave. You can also change the hand itself to become an indicator; since we’re using a servo, you can control the state, or how much, the servo rotates. You can make the hand move to different positions depending on whether it’s cloudy or sunny and make the servo rotate to that predefined position when the weather changes.

## Custom Development Setup
In order to customize the microcontroller, you have to re-flash the NodeMCU again. Below are the steps that you need to do.

### For Windows:
1. Set up a new virtual environment in Python
- make sure you have python installed (open Command Prompt and type in `python`; if it opens python shell then you've confirmed Python is accessible in your Path; otherwise reinstall Python and ensure you check the box to add it to your system's path environment variable)
- locate the directory you want the virtual environment to be installed in
- in the Windows Command Prompt, enter "python -m venv venv"
  - This command invokes the python module *venv* (first parameter) and creates it inside a directory named *venv* (second parameter)
- then run `.\venv\Scripts\Activate.bat`
  - This command activates the virtual environment; you should now see your command prompt prepended with **(venv)**
- IF using Power Shell (instead of command prompt), use `.\venv\Scripts\Activate.ps1`
  - This command activates the virtual environment; you should now see your command prompt prepended with **(venv)**
- ⚠️ensure that servo is not connected to the NodeMCU before next step
2. Installing esphome
- enter `pip install esphome`
1. Download or `git clone` the [repo](https://github.com/codycodes/gix-mkrfridays-iot/archive/master.zip) and extract it anywhere (best is to put it in same folder as your venv)
- in the standalone folder, right-click and create new text document.
- copy and paste these into it.
    ap_ssid: "Servo Test Fallback Hotspot"
    ap_pass: "test12341234"
    ota_pass: "test12341234"
- rename file name to "secrets.yaml" (ensure the file extension is `.yaml` and **not** `.txt`)
4. Run!
- in Command Prompt, type and run `cd *path to the standalone folder*`
- then `esphome servo.yaml run`
- it should start installing 
- DONE!
5. You can now develop your own custom esphome components! Get started on [esphome.io](http://esphome.io)
### For macOS/Linux
1. Ensure you have python3 [installed](https://docs.python-guide.org/starting/install3/osx/)
2. Open your favorite terminal app
3. run `./install.sh`
4. run `./run.sh`
    - You can replace the `servo.yaml` file here with your own configuration!
5. You can now develop your own custom esphome components! Get started on [esphome.io](http://esphome.io)

# Remote Control (via Azure IoT Hub)
## Prerequisites
### Hardware
One of the following boards:
- ESP8266 based boards with esp8266/arduino
- ESP32 based boards with espressif/arduino-esp32  
and a...
- USB cable for data transfer or other flashing hardware

### Software
- [python3.5+](https://www.python.org/downloads/) Installed and accessible via your [PATH](https://www.tutorialspoint.com/python/python_environment.htm) environment variable
- [git](https://git-scm.com)
- [Arduino IDE](https://www.arduino.cc/en/main/software)

## Setup Instructions
If any of these steps fail please double check these instructions, open an issue [here](https://github.com/codycodes/gix-mkrfridays-iot/issues/new/choose), and see if there's a solution to the issue on the official [Azure IoT Arduino repo](https://github.com/Azure/azure-iot-arduino)


### ESP8266
#### Installing Azure IoT Arduino libs
1. Open up the Arduino IDE and go to **Tools > Manage Libraries**
    ![mng_lib](./assets/arduino/10.png)
2. Install the following libraries through the Arduino IDE Library Manager:  
  `AzureIoTHub`  
  `AzureIoTUtility`  
  `AzureIoTProtocol_MQTT`  
  `AzureIoTProtocol_HTTP`  
#### Install board into Arduino IDE
 1. (Windows) Start Arduino IDE and go to **File > Preferences**  
    (macOS) Start Arduino IDE and go to **Arduino > Preferences**  
 2. In the *Additional Board Manager URLs:* field, enter `http://arduino.esp8266.com/stable/package_esp8266com_index.json`  
   ![boards_url](./assets/arduino/1.png)
   You can add multiple URLs for boards, separating each with a comma `,`
 3. Go to **Tools > Board: *currently selected board*** and open **Boards Manager**.  
   ![boards_mgr](./assets/arduino/3.png)
    - In **Boards Manager**, search for *esp8266* and install esp8266 version **2.5.2 or later**.
     ![boards_mgr](./assets/arduino/5.png)
 4. Select your ESP8266 board from **Tools > Board: *currently selected board*** menu after installation. After selection, the menu should read **Tools > Board: "Generic ESP8266 Module"**:
     ![boards_mgr](./assets/arduino/7.png)
#### Finish board setup via python script
 1. Clone this repo using: 
    
    `git clone "https://github.com/codycodes/gix-mkrfridays-iot.git"`

      - Note: if you already did this before you don't need to do it again! In that case skip to step 2.
 2. Open a terminal and `cd` to the directory you cloned the repo to. The path will be something like `/dir/to/clone/gix-mkrfridays-iot`, where `/dir/to/clone` is where you cloned the repo to.
    - You will also want to fetch
 3. Open iot_configs.h and update WiFi SSID and Password.
    - Make sure you are using a WiFi network that does not require additional manual steps after connection, such as opening a web browser.
 4. Open and run 'script.py' which would automatically locate your board's Arduino.h and platform.txt and make changes to it.
#### Upload code to Arduino
1. Choose the example you would like to run from *quickstarts* folder located in **gix-mkrfridays-iot/arduino/quickstarts**. Open the `.ino` file in the Arduino IDE (double-click it from your file explorer).
2. Ensure that the correct serial port and board are selected.
3. Plug the Arduino in. Run the sample by clicking upload.

### ESP32
