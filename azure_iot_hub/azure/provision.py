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
    STORAGE_ACCT_NAME = IOT_RESOURCES['STORAGE_ACCT_NAME']
    print(f"IOT_HUB_NAME received: {IOT_HUB_NAME}")
    print(f"STORAGE_ACCT_NAME received: {STORAGE_ACCT_NAME}")
except (OSError, IOError) as e:
    IOT_RESOURCES = {}
    IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-{random.randint(1,100000):05}"
    IOT_RESOURCES['IOT_HUB_NAME'] = IOT_HUB_NAME
    print(f"IOT_HUB_NAME doesn't exist, created: {IOT_HUB_NAME}")
    # Must be <= 24 chars and alphanumeric only
    STORAGE_ACCT_NAME = f"storage{random.randint(1,100000):05}"
    IOT_RESOURCES['STORAGE_ACCT_NAME'] = STORAGE_ACCT_NAME
    print(f"STORAGE_ACCT_NAME doesn't exist, created: {STORAGE_ACCT_NAME}")
    pickle.dump(IOT_RESOURCES, open("resource_state.pickle", "wb"))


# TODO: store in a pickle
# The name of the serverless app which holds the functions
# Should be globally unique
FUNCTION_APP_NAME = f"{RESOURCE_GROUP_NAME}" \
                    f"-app-{random.randint(1,100000):05}"

# TODO: remove when done testing
FUNCTION_APP_NAME = f"porg-app2"
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
CREATE_RBAC_SP = True

# Determines whether to create a static site dashboard
CREATE_STATIC_SITE = True

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
    print("Finishing hub creation")
    time.sleep(10)

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
        # TODO: get the type of device to copy from the list of names here
        # Or just set the type of device to copy
        with open(
                '../device_connection_strings.csv', 'r', newline='') \
                as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # set the device name as the func name
                device_id = row[0]
                shutil.copytree(
                    f'../templates/led_matrix_esp32_iot_hub',
                    f'./{device_id}')
                update_line_file(
                    f'./{device_id}/__init__.py',
                    f'CONNECTION_STRING = ',
                    f"CONNECTION_STRING ="
                    f" '{c2d_connection_string['connectionString']}'"
                )
                update_line_file(
                    f'./{device_id}/__init__.py',
                    f'DEVICE_ID = ',
                    f"DEVICE_ID = '{device_id}'"
                )
        time.sleep(10)

    print('Deploying function to Azure...')
    os.system(f'func azure functionapp publish {FUNCTION_APP_NAME}')
    os.chdir('../')


if CREATE_SERVERLESS_APP or CREATE_FUNCTIONS:
    create_func_app()


# TODO: store the output in a pickle
# The az_cli command wasn't working so revert to os.system
# and store output in a json file
# TODO: make this a Path object and be careful; use full paths
# TODO: check if it exists here first
# Create/fetch RBAC and request an OAuth token
if CREATE_RBAC_SP:
    os.system(
        f'az ad sp create-for-rbac --sdk-auth'
        f' --name {RBAC_SERVICE_PRINCIPAL_NAME} > local-sp.json')
    print("Waiting a minute for RBAC to finish updating...")
    time.sleep(60)

if WRITE_FUNCTION_URLS:
    with open('local-sp.json') as json_file:
        result = json.load(json_file)

    SUBSCRIPTION_ID = result['subscriptionId']
    TENANT_ID = result['tenantId']
    CLIENT_ID = result['clientId']
    CLIENT_SECRET = result['clientSecret']
    RESOURCE = 'https://management.azure.com'
    auth_body = {'grant_type': 'client_credentials',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'resource': RESOURCE, }
    response = requests.post(
            f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/token',
            data=auth_body)
    aad_token = response.json()['access_token']

    # TODO: catch keyerrors and write messages
    with open('device_function_urls.csv', 'w', newline='') as csvfiles:
        writer = csv.writer(csvfiles)
        for device_id in IOT_DEVICE_NAMES:
            r = requests.post(
                    f'https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}'
                    f'/resourceGroups/{RESOURCE_GROUP_NAME}'
                    f'/providers/Microsoft.Web/sites/{FUNCTION_APP_NAME}'
                    f'/functions/{device_id}/listKeys?api-version=2018-02-01',
                    headers={'Authorization': f'Bearer {aad_token}'})
            code = r.json()['default']
            url = f'https://{FUNCTION_APP_NAME}.azurewebsites.net/api' \
                f'/{device_id}?code={code}'
            writer.writerow([device_id, url])
        print("Successfully wrote device function URLs")


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
