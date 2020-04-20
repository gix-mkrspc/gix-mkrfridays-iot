echo "Ensure you have Python3 installed on your machine and it's located in your \$PATH variable"

# create a venv in the directory you run this script from
mkdir ./esphome
python3 -m venv ./esphome
source ./esphome/bin/activate
pip install esphome tornado esptool