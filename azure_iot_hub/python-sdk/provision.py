from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient
from azure.cli.core import get_default_cli

import os
import random
import subprocess
import json
import csv
import pickle


# What does this script do?
# The main purpose of this script is to provision IoT Hub resources on Azure

def az_cli(command):
    args = command.split()
    print(args)
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise cli.result.error
    return True


# The RESOURCE_GROUP_NAME/RESOURCE_GROUP_LOCATION
#  are where your resources will be created and referenced
RESOURCE_GROUP_NAME = "MKRPSC-iot-porg"
RESOURCE_GROUP_LOCATION = "West US"

# TODO: this can be stored in a pickle; check if it exists
# Can be merged into the below CREATE_IOT_HUB to set it automatically
# NOTE: IOT_HUB_NAME must be unique globally across Azure
# IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-{random.randint(1,100000):05}"


#create a new random IOT_HUB_NAME and pickle.dump 
try:
    IOT_HUB_NAME = pickle.load(open("IOT_pickle.pickle", "rb"))
    print("IOT_HUB_NAME received")
except (OSError, IOError) as e:
    IOT_HUB_NAME= f"{RESOURCE_GROUP_NAME}-{random.randint(1,100000):05}"
    pickle.dump(IOT_HUB_NAME, open("IOT_pickle.pickle", "wb"))
    print("IOT_HUB_NAME DNE, created new names: " + IOT_HUB_NAME )





# Setting CREATE_IOT_HUB to True/False will either create an IOT HUB or not.
# If you set it to false it will use the IOT_HUB_NAME variable
#  to assume that the hub exists
CREATE_IOT_HUB = True

# If you have a list of device identifiers, you can pass these in as a file
#   in the following format:
#   device_id1
#   device_id2
#   ...etc
# TODO: update file name
# Otherwise, devices will be created with random identifiers. All identifiers
# and connection strings will be stored in a file called
# INSERT FILE NAME HERE.txt

# TODO: this should be implemented and tested
USE_RANDOM_IDENTIFIERS = False

# TODO: wrap this in a try and also use WITH
IOT_database = open("IoT_device_name.txt", "r")
IOT_database_list = IOT_database.read()

IOT_DEVICE_NAMES = IOT_database_list.split('\n')

# The number of devices you want to create.
# Only applies if you set USE_RANDOM_IDENTIFIERS to True
# Otherwise it will be the length of IOT_DEVICE_NAMES
IOT_HUB_NUM_DEVICES = len(IOT_DEVICE_NAMES)

# The SKU; by default it's set for free tier
IOT_HUB_SKU = "F1"
IOT_HUB_PARTITION_COUNT = "2"

# Only applies if you set USE_RANDOM_IDENTIFIERS to True
IOT_HUB_DEVICE_PREFIX = "device"

resource_client = get_client_from_cli_profile(ResourceManagementClient)

# Provision the resource group.
rg_result = resource_client.resource_groups.create_or_update(
    f"{RESOURCE_GROUP_NAME}",
    {
        "location": f"{RESOURCE_GROUP_LOCATION}"
    }
)

print(
    f"Provisioned/updated resource group {rg_result.name} in the"
    f" {rg_result.location} region")

# install extension if not already installed
print('Checking az cli iot-hub extension...')
az_cli('extension add --name azure-iot')

if CREATE_IOT_HUB:
    print('Creating iot hub')
    direct_output = az_cli(
        f"iot hub create -n {IOT_HUB_NAME}"
        f" --resource-group {RESOURCE_GROUP_NAME}"
        f" --sku {IOT_HUB_SKU} --verbose"
        f" --partition-count {IOT_HUB_PARTITION_COUNT}")

# TODO: have an option for whether the user is providing
#  a file with strings on each line
# with the identifiers for the devices
#  or if they just have a finite number defined with a prefix
# TODO: if there's a prefix just append the number i to the end of it
#  OR if it's from the file just use that name
for i in range(IOT_HUB_NUM_DEVICES):
    if IOT_DEVICE_NAMES:
        # TODO: this probably needs to be redone
        device_name = IOT_DEVICE_NAMES[i]
    else:
        device_name = f"{IOT_HUB_DEVICE_PREFIX}-{i}"
    az_cli(
        f"iot hub device-identity create"
        f" -n {IOT_HUB_NAME} -d {device_name}")

with open('output.csv', 'w', newline='') as csvfiles:
    writer = csv.writer(csvfiles)
    for device_name in IOT_DEVICE_NAMES:
        direct_output = az_cli(
            f"iot hub device-identity show-connection-string"
            f" -d {device_name} -n {IOT_HUB_NAME}")
        writer.writerow([device_name, direct_output["connectionString"]])
