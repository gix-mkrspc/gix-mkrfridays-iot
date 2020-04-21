echo "Ensure you have Python3 installed on your machine and it's
 located in your \$PATH variable. Now installing..."
sleep 5

# create a venv in the directory you run this script from
mkdir ./esphome
python3 -m venv ./esphome
source ./esphome/bin/activate
pip install esphome tornado esptool

echo "






 ******** Install Complete! ********
 
 please create a file called secrets.yaml inside the same directory
 this script is run in! Anywhere it says !secret you need to create a key/value
 pair where the key is what comes after secret in servo.yaml and the value is
 the private information. Here's an example entry inside secrets.yaml:

 ap_ssid: \"super secret ap ssid\"
 "