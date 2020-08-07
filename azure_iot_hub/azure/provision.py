from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient
from azure.cli.core import get_default_cli

import os
import sys
import random
import subprocess
import json
import csv
import pickle
import time
import requests
import fileinput
import shutil
from Device import *

# TODO: Follow the official code guidelines:
# https://azure.github.io/azure-sdk/python_introduction.html

# What does this script do?
# The main purpose of this script is to provision IoT Hub resources on Azure


def az_cli(command):
    args = command.split()
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

RBAC_SERVICE_PRINCIPAL_NAME = "iotporgpython3"


# NOTE: IOT_HUB_NAME must be unique withing your resouroce group
try:
    IOT_RESOURCES = pickle.load(open("resource_state.pickle", "rb"))
    IOT_HUB_NAME = IOT_RESOURCES['IOT_HUB_NAME']
    print(f"IOT_HUB_NAME received: {IOT_HUB_NAME}")
    STORAGE_ACCT_NAME = IOT_RESOURCES['STORAGE_ACCT_NAME']
    print(f"STORAGE_ACCT_NAME received: {STORAGE_ACCT_NAME}")
    FUNCTION_APP_NAME = IOT_RESOURCES['FUNCTION_APP_NAME']
    print(f"FUNCTION_APP_NAME received: {FUNCTION_APP_NAME}")
except (OSError, IOError) as e:
    IOT_RESOURCES = {}
    IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-{random.randint(1,100000):05}"
    IOT_RESOURCES['IOT_HUB_NAME'] = IOT_HUB_NAME
    print(f"IOT_HUB_NAME didn't exist, created: {IOT_HUB_NAME}")
    # Must be <= 24 chars and alphanumeric only
    STORAGE_ACCT_NAME = f"storage{random.randint(1,100000):05}"
    IOT_RESOURCES['STORAGE_ACCT_NAME'] = STORAGE_ACCT_NAME
    print(f"STORAGE_ACCT_NAME didn't exist, created: {STORAGE_ACCT_NAME}")
    FUNCTION_APP_NAME = f"{RESOURCE_GROUP_NAME}" \
                        f"-app-{random.randint(1,100000):05}"
    IOT_RESOURCES['FUNCTION_APP_NAME'] = FUNCTION_APP_NAME
    print(f"FUNCTION_APP_NAME didn't exist, created: {FUNCTION_APP_NAME}")
    pickle.dump(IOT_RESOURCES, open("resource_state.pickle", "wb"))


DEVICE_DIR_MAPPINGS = {
    'blink': 'blink_onboard_esp8266_iot_hub',
    'screen': 'led_matrix_esp32_iot_hub',
    'porg': 'porg_esp8266_iot_hub',
    'servo': 'servo_esp8266_iot_hub',
    'generic': 'generic_esp8266_iot_hub'
}

# find locations with az functionapp list-consumption-locations
FUNCTION_APP_LOCATION = "westus"

STORAGE_ACCT_LOCATION = "westus"

# Determines whether to create an IoT Hub
# Looks for existing IoT Hub name in pickle if not created
CREATE_IOT_HUB = True

# Determines whether to create or use existing IoT Devices
# Looks for existing devices in device_connection_strings.csv
CREATE_IOT_DEVICES = True

# Determines whether to create serverless app
CREATE_SERVERLESS_APP = True

# Determines whether to create functions inside
# existing (in this dir) named serverless app
CREATE_FUNCTIONS = True

# Determines whether to fetch function URL api keys
WRITE_FUNCTION_URLS = True

# Needed to access Azure REST API; if you have
#  local-sp.json in this dir you don't need to run this
CREATE_RBAC_SP = False

# Determines whether to create a static site dashboard
CREATE_STATIC_SITE = True

# If you have a list of device identifiers, you can pass these in as a file
#   in the following format:
#   device_id1
#   device_id2
#   ...etc
# Otherwise, devices will be created with random identifiers. All identifiers
# and connection strings will be stored in a file called
# device_connection_strings.csv

# TODO: wrap this in a try and also use WITH
IOT_database = open("IoT_device_name.txt", "r")
IOT_database_list = IOT_database.read()

# Process device names & types
IOT_DEVICES = IOT_database_list.split('\n')
IOT_DEVICE_TYPES = [device.split(',') for device in IOT_DEVICES]
IOT_DEVICES = {}

for entry in IOT_DEVICE_TYPES:
    name = entry[0].strip()
    if len(entry) > 1:
        for kind in entry[1:]:
            device = Device(name, kind.strip())
            IOT_DEVICES[device.device_name] = device
    else:
        device = Device(name)
        IOT_DEVICES[device.device_name] = device

# The SKU; by default it's set for free tier
IOT_HUB_SKU = "F1"
IOT_HUB_PARTITION_COUNT = "2"

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
    print("Finishing hub creation")
    time.sleep(10)

# TODO: have an option for whether the user is providing
#  a file with strings on each line
# with the identifiers for the devices
#  or if they just have a finite number defined with a prefix
# TODO: if there's a prefix just append the number i to the end of it
#  OR if it's from the file just use that name
if CREATE_IOT_DEVICES:
    for device_name in IOT_DEVICES:
        az_cli(
            f"iot hub device-identity create"
            f" -n {IOT_HUB_NAME} -d {device_name}")

    #  Get device connection strings
    with open('device_connection_strings.csv', 'w', newline='') as csvfiles:
        writer = csv.writer(csvfiles)
        for device_name in IOT_DEVICES:
            direct_output = az_cli(
                f"iot hub device-identity show-connection-string"
                f" -d {device_name} -n {IOT_HUB_NAME}")
            connection_string = direct_output["connectionString"]
            IOT_DEVICES[device_name].connection_string = connection_string
            writer.writerow([device_name, connection_string])


def update_line_file(
        file_path, str_line_to_update, str_replacement, comment_only=False,
        comment_str=None):
    '''
    Updates a line on a file with a replacement line or comments it out

    :param file_path: The path to the file
    :type file_path: str
    :param str_to_update: The string which will be replaced
    :type str_to_update str:
    :param str_replacement: The string which replace the line of str_to_update
    :type str_replacement str:
    :param comment_only: Determines whether to replace or only comment out a
    line
    :type comment_only boolean:
    :param comment_str: Str to use for a comment if commenting
    :type comment_only str:
    :raises: :class:`FileNotFound`: File couldn't be opened

    :returns: whether the string was replaced in the file or it was commented
    out
    :rtype: boolean
    '''
    file_modified = False
    for line in fileinput.input(file_path, inplace=True):
        if line.startswith(str_line_to_update):
            if comment_only:
                line = f"{comment_str} {line}"
                file_modified = True
            elif line.rstrip() != str_replacement:
                line = f"{str_replacement}\n"
                file_modified = True
        sys.stdout.write(line)

    return file_modified


def create_func_app():
    if CREATE_SERVERLESS_APP:
        print("Creating serverless app")
        print("Creating storage account")
        os.system(f'func init {FUNCTION_APP_NAME} --python')
        os.chdir(FUNCTION_APP_NAME)
        az_cli(
            f'storage account create --name {STORAGE_ACCT_NAME}'
            f' --location {STORAGE_ACCT_LOCATION}'
            f' --resource-group {RESOURCE_GROUP_NAME}'
            f' --sku Standard_LRS'
        )
        print("Storage account created; now creating function app")
        az_cli(
            f'functionapp create --resource-group {RESOURCE_GROUP_NAME}'
            f' --os-type Linux'
            f' --consumption-plan-location {FUNCTION_APP_LOCATION}'
            f' --runtime python --runtime-version 3.7 --functions-version 2'
            f' --name {FUNCTION_APP_NAME}'
            f' --storage-account {STORAGE_ACCT_NAME}')
        print('Sleeping for ten seconds to allow'
              ' cloud resources to provision...')
        time.sleep(10)
    else:
        # Switch to this dir anyways
        os.chdir(FUNCTION_APP_NAME)
    # TODO: fix this for Windows using the Path lib
    if CREATE_FUNCTIONS:
        print("Creating functions")
        # overwrite the generated requirements.txt
        shutil.copyfile(
            '../templates/requirements.txt',
            './requirements.txt'
        )
        # grab the service connection string
        c2d_connection_string = az_cli(
            f'iot hub show-connection-string'
            f' --name {IOT_HUB_NAME} --policy-name service'
        )
        for d in IOT_DEVICES:
            device = IOT_DEVICES[d]
            # set the device name as the func name
            shutil.copytree(
                f'../templates/{DEVICE_DIR_MAPPINGS[device.kind]}',
                f'./{device.device_name}')
            update_line_file(
                f'./{device.device_name}/__init__.py',
                f'CONNECTION_STRING = ',
                f"CONNECTION_STRING ="
                f" '{c2d_connection_string['connectionString']}'"
            )
            update_line_file(
                f'./{device.device_name}/__init__.py',
                f'DEVICE_ID = ',
                f"DEVICE_ID = '{device.device_name}'"
            )
        time.sleep(10)

    print('Deploying function to Azure...')
    os.system(f'func azure functionapp publish {FUNCTION_APP_NAME}')
    os.chdir('../')


if CREATE_SERVERLESS_APP or CREATE_FUNCTIONS:
    create_func_app()
    with open('device_function_urls.csv', 'w', newline='') as csvfiles:
        writer = csv.writer(csvfiles)
        for d in IOT_DEVICES:
            device = IOT_DEVICES[d]
            device.function_url = f"https://{FUNCTION_APP_NAME}.azurewebsites.net" \
                                f"/api/{device.device_name}"
            writer.writerow([device.device_name, device.function_url])
    pickle.dump(IOT_DEVICES, open("devices.pickle", "wb"))
    print("Successfully wrote device function URLs")
    for d in IOT_DEVICES:
        device = IOT_DEVICES[d]
        print(f'device name: {device.name} -> url: {device.function_url}')

if CREATE_STATIC_SITE:
    # Generate site
    # TODO: this needs to be tested for cross platform
    os.system('python create_launch_site.py')
    print('Generating static site for dashboard...')
    time.sleep(10)
    # Create static site on Azure
    az_cli(
        f'storage blob service-properties update'
        f' --account-name {STORAGE_ACCT_NAME} --static-website'
        f' --index-document index.html')

    # Upload files from generated_site folder
    az_cli(
        f"storage blob upload-batch"
        f" -s generated_site -d $web"
        f" --account-name {STORAGE_ACCT_NAME}")

    # Get URL
    endpoints = az_cli(
        f'storage account show -n {STORAGE_ACCT_NAME}'
        f' -g {RESOURCE_GROUP_NAME} --query "primaryEndpoints"')
    print(f"Please view dashboard at: {endpoints['web']}")
