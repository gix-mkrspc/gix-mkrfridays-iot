from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient
from azure.cli.core import get_default_cli

import os
import random
import subprocess
import json


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

# What does this script do?
# The main purpose of this script is to provision IoT Hub resources on Azure


# Setting CREATE_IOT_HUB to True/False will either create an IOT HUB or not.
# If you set it to false it will use the IOT_HUB_NAME variable to assume that the hub exists
CREATE_IOT_HUB = False

# The RESOURCE_GROUP_NAME/RESOURCE_GROUP_LOCATION are where your resources will be created
# and referenced
RESOURCE_GROUP_NAME = "MKRPSC_iot-porg"
RESOURCE_GROUP_LOCATION = "West US"

IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-iothub"
# # TODO: This should be grabbing from a text file or other source so that we have
# # idempotency/consistent runs
# IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-{random.randint(1,100000):05}"

IOT_HUB_NAME = "internet-of-porg"

# If you have a list of device identifiers, you can pass these in as a file
#   in the following format:
#   device_id1
#   device_id2
#   ...etc
# TODO: update file name
# Otherwise, devices will be created with random identifiers. All identifiers
# and connection strings will be stored in a file called INSERT FILE NAME HERE.txt
USE_RANDOM_IDENTIFIERS = False

# TODO: wrap this in a try and also use WITH
# IOT_database= open("IoT_device_name.txt", "r")
# IOT_database_list=IOT_database.read()

# # TODO: may require rstrip() after split to work on windows + macOS + linux
# # see https://bit.ly/2ytd1NN since there may be a line feed as well

# IOT_DEVICE_NAMES=IOT_database_list.split('\n')     #This will be a list of string

# Used to name the devices upon provision

# IOT_DEVICE_NAMES= ['cody','justin','joey]


# The number of devices you want to create.
# Only applies if you set USE_RANDOM_IDENTIFIERS to True
# Otherwise it will be the length of IOT_DEVICE_NAMES
IOT_HUB_NUM_DEVICES = 0

# The SKU; by default it's set for free tier
IOT_HUB_SKU = "F1"
IOT_HUB_PARTITION_COUNT = "2"

# Only applies if you set USE_RANDOM_IDENTIFIERS to True
IOT_HUB_DEVICE_PREFIX = "device"

# Obtain the management object for resources, using the credentials from the CLI login.
resource_client = get_client_from_cli_profile(ResourceManagementClient)

# Provision the resource group.
rg_result = resource_client.resource_groups.create_or_update(
    f"{RESOURCE_GROUP_NAME}",
    {
        "location": f"{RESOURCE_GROUP_LOCATION}"
    }
)

print(
    f"Provisioned/updated resource group {rg_result.name} in the {rg_result.location} region")

# install extension if not already installed
print('Checking az cli iot-hub extension...')

az_cli('extension add --name azure-iot')

if CREATE_IOT_HUB:
    print('Creating iot hub')

    az_cli([az iot hub create - {IOT_HUB_NAME} - r {RESOURCE_GROUP_NAME} - s {IOT_HUB_SKU} - v - p {IOT_HUB_PARTITION_COUNT}])
   # az_cli([az iot hub create -{IOT_HUB_NAME} --resource-group {RESOURCE_GROUP_NAME} --sku {IOT_HUB_SKU} --verbose --partition-count IOT_HUB_PARTITION_COUNT])

    output_clean = direct_output.decode('utf8').replace("\n", '')
    iot_hub_output = json.loads(output_clean)

    # I think ithis is fine since it has all the info needed!
    with open(f'{IOT_HUB_NAME}.json', 'w') as json_file:
        json.dump(iot_hub_output, json_file)

# TODO: create a CSV with the following:
# Device ID, Connection String

# print(iot_hub_output["id"])
# iot_hub_output is a parsed json
# data can be extracted for function app

# TODO: have an option for whether the user is providing a file with strings on each line
# with the identifiers for the devices or if they just have a finite number defined with a prefix
# for i in range(IOT_HUB_NUM_DEVICES):
#     device_name = IOT_HUB_NAME[i]
#     # TODO: use az_cli function REMEMBER TO REMOVE AZ from command though!
#     az_cli(f"az iot hub device-identity create -n {IOT_HUB_NAME} "
#             f"-d {device_name}"
#             )


# TODO: if there's a prefix just append the number i to the end of it
#  OR if it's from the file just use that name
for i in range(IOT_HUB_NUM_DEVICES):
    if IOT_DEVICE_NAMES:
        # TODO: this probably needs to be redone
        device_name = IOT_DEVICE_NAMES[i]
    else:
        device_name = f"{IOT_HUB_DEVICE_PREFIX}-{i}"
    az_cli(
        f"iot hub device-identity create -n {IOT_HUB_NAME} -d {device_name}")
    # direct_output = subprocess.check_output(['az', 'iot', 'hub', 'device-identity', 'create', '-n', \
    #                                     IOT_HUB_NAME, '-d', device_name])
    output_clean = direct_output.decode('utf8').replace("\n", '')
    device_output = json.loads(output_clean)
    # TODO: get the right device parameters here using
    #     az_cli(f"iot hub device-identity show-connection-string -d {device_name} -n {IOT_HUB_NAME}")
    with open(f'{device_name}.json', 'w') as json_file:
        json.dump(device_output, json_file)
    #output_clean = direct_output.decode('utf8').replace("\n", '')
    #device_output = json.loads(output_clean)
    # output from each device
    # TODO: append device name and connection string to file here

connec_string = []

for i in range(IOT_HUB_NUM_DEVICES):
    device_name = str(IOT_DEVICE_NAMES[i])

    az_cli(
        f"iot hub device-identity show-connection-string -d {device_name} -n {IOT_HUB_NAME}")
    # connec_string[j]= az_cli("az iot hub device-identity show-connection-string")

# az extension add --name azure-iot
# az iot hub monitor-events --hub-name {IOT_HUB_NAME}
