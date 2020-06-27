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
import requests

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

# NOTE: IOT_HUB_NAME must be unique globally across Azure
try:
    IOT_HUB_NAME = pickle.load(open("IOT_pickle.pickle", "rb"))
    print(f"IOT_HUB_NAME received: {IOT_HUB_NAME}")
except (OSError, IOError) as e:
    IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-{random.randint(1,100000):05}"
    pickle.dump(IOT_HUB_NAME, open("IOT_pickle.pickle", "wb"))
    print(f"IOT_HUB_NAME doesn't exist, created: {IOT_HUB_NAME}")

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

# Setting CREATE_SERVERLESS_APP to True/False will
# either create a serverless app or not
CREATE_SERVERLESS_APP = True

# Setting CREATE_FUNCTIONS to True/False will
# determine whether to use device list
# to create functions inside a serverless app or not
CREATE_FUNCTIONS = True

CREATE_RBAC_SP = True

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
        # grab the service connection string
        c2d_connection_string = az_cli(
            f'iot hub show-connection-string'
            f' --name {IOT_HUB_NAME} --policy-name service'
        )
        c2d_connection_string = c2d_connection_string['connectionString']
        print(c2d_connection_string)
        with open(
                '../device_connection_strings.csv', 'r', newline='') \
                as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # set the device name as the func name
                os.system(
                    f'func new --name {row[0]}'
                    f' --template "HTTP trigger"')
            time.sleep(10)

    print('Deploying function to Azure...')
    os.system(f'func azure functionapp publish {FUNCTION_APP_NAME}')
    os.chdir('../')


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
