from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient
from azure.cli.core import get_default_cli

import os
import random
import subprocess
import json
import csv
import pickle
import time


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
RESOURCE_GROUP_NAME = "MKRSPC-iot-porg"
RESOURCE_GROUP_LOCATION = "West US"

# NOTE: IOT_HUB_NAME must be unique globally across Azure
try:
    IOT_HUB_NAME = pickle.load(open("IOT_pickle.pickle", "rb"))
    print("IOT_HUB_NAME received")
except (OSError, IOError) as e:
    IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-{random.randint(1,100000):05}"
    pickle.dump(IOT_HUB_NAME, open("IOT_pickle.pickle", "wb"))
    print("IOT_HUB_NAME DNE, created new name: " + IOT_HUB_NAME)

# TODO: store in a pickle
# The name of the serverless app which holds the functions
# Should be globally unique
FUNCTION_APP_NAME = f"{RESOURCE_GROUP_NAME}" \
                    f"-app-{random.randint(1,100000):05}"

# TODO: remove when done testing
FUNCTION_APP_NAME = f"porg-app2"
# find locations with az functionapp list-consumption-locations
FUNCTION_APP_LOCATION = "westus"

# Must be <= 24 chars and alphanumeric only
STORAGE_ACCT_NAME = f"storage{random.randint(1,100000):05}"
STORAGE_ACCT_LOCATION = "westus"

# Setting CREATE_IOT_HUB to True/False will either create an IOT HUB or not.
# If you set it to false it will use the IOT_HUB_NAME variable
#  to assume that the hub exists
CREATE_IOT_HUB = True

# Setting CREATE_IOT_DEVICES to True/False will
# either create IoT Devices or not
CREATE_IOT_DEVICES = True

# Setting CREATE_IOT_DEVICES to True/False will
# either create a serverless app or not
CREATE_SERVERLESS_APP = True

# If you have a list of device identifiers, you can pass these in as a filer
#   in the following format:
#   device_id1
#   device_id2
#   ...etc
# Otherwise, devices will be created with random identifiers. All identifiers
# and connection strings will be stored in a file called
# device_connection_strings.csv

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
if CREATE_IOT_DEVICES:
    for i in range(IOT_HUB_NUM_DEVICES):
        if IOT_DEVICE_NAMES:
            # TODO: this probably needs to be redone
            device_name = IOT_DEVICE_NAMES[i]
        else:
            device_name = f"{IOT_HUB_DEVICE_PREFIX}-{i}"
        az_cli(
            f"iot hub device-identity create"
            f" -n {IOT_HUB_NAME} -d {device_name}")

    with open('device_connection_strings.csv', 'w', newline='') as csvfiles:
        writer = csv.writer(csvfiles)
        for device_name in IOT_DEVICE_NAMES:
            direct_output = az_cli(
                f"iot hub device-identity show-connection-string"
                f" -d {device_name} -n {IOT_HUB_NAME}")
            writer.writerow([device_name, direct_output["connectionString"]])


def create_func_app():
    if CREATE_SERVERLESS_APP:
        os.system(f'func init {FUNCTION_APP_NAME} --python')
        os.chdir(FUNCTION_APP_NAME)
        print(os.getcwd())
    else:
        # change to the dir so we can create functions
        os.chdir(FUNCTION_APP_NAME)
    # TODO: fix this for Windows using the Path lib
    with open('../device_connection_strings.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # set the device name as the func name
            os.system(f'func new --name {row[0]} --template "HTTP trigger"')
    # TODO: actual deployment of the function app
    # requires creating a storage group (globally unique)
    # deploy serverless app
    # since the az_cli function splits tokens we run this
    # from the command line to avoid issues with spaces
    az_cli(
        f'storage account create --name {STORAGE_ACCT_NAME}'
        f' --location {STORAGE_ACCT_LOCATION}'
        f' --resource-group {RESOURCE_GROUP_NAME}'
        f' --sku Standard_LRS'
    )

    direct_output = az_cli(
        f'functionapp create --resource-group {RESOURCE_GROUP_NAME}'
        f' --os-type Linux'
        f' --consumption-plan-location {FUNCTION_APP_LOCATION}'
        f' --runtime python --runtime-version 3.7 --functions-version 2'
        f' --name {FUNCTION_APP_NAME}'
        f' --storage-account {STORAGE_ACCT_NAME}')
    print('Sleeping for ten seconds to allow cloud resources to provision...')
    time.sleep(10)
    os.system(f'func azure functionapp publish {FUNCTION_APP_NAME} --python')
    # TODO: get function secrets via REST API
    # https://bit.ly/3d9Yk0A
    # TODO: Follow the official code guidelines:
    # https://azure.github.io/azure-sdk/python_introduction.html

create_func_app()
