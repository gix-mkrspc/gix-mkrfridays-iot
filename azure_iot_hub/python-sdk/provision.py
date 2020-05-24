# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient

import os
import random
import subprocess
import json

RESOURCE_GROUP_NAME = "MKRPSC_iot-porg"
RESOURCE_GROUP_LOCATION = "West US"


# IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-iothub"
# TODO: This should be grabbing from a text file or other source so that we have
# idempotency/consistent runs
#IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-{random.randint(1,100000):05}"

IOT_database= open("IoT_device_name.txt", "r")
IOT_database_list=IOT_database.read()
IOT_HUB_NAME=IOT_database_list.split('\n' )     #This will be a list of string


IOT_HUB_SKU = "F1" # free tier
IOT_HUB_PARTITION_COUNT = "2" # free tier

IOT_HUB_NUM_DEVICES = len(IOT_HUB_NAME)  #read the length of the name txt


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

# Within the ResourceManagementClient is an object named resource_groups,
# which is of class ResourceGroupsOperations, which contains methods like
# create_or_update.
#
# The second parameter to create_or_update here is technically a ResourceGroup
# object. You can create the object directly using ResourceGroup(location=LOCATION)
# or you can express the object as inline JSON as shown here. For details,
# see Inline JSON pattern for object arguments at
# https://docs.microsoft.com/azure/developer/python/azure-sdk-overview#inline-json-pattern-for-object-arguments.

print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")

# install extension if not already installed

print('Checking az cli iot-hub extension...')
os.system('az extension add --name azure-iot')
print('Creating iot hub')


#use a for loop to create n IoT devices in the database
for i in range (IOT_HUB_NUM_DEVICES)
    os.system(f"az iot hub create --name {IOT_HUB_NAME[i]} "
         f"--resource-group {RESOURCE_GROUP_NAME} --sku {IOT_HUB_SKU} --verbose "
         f"--partition-count {IOT_HUB_PARTITION_COUNT}"
         )



# The return value is another ResourceGroup object with all the details of the
# new group. In this case the call is synchronous: the resource group has been
# provisioned by the time the call returns.

# Optional line to delete the resource group
#resource_client.resource_groups.delete("PythonSDKExample-ResourceGroup-rg")

#repeated?????????????????????

#os.system(f"az iot hub create --name {IOT_HUB_NAME} "
#        f"--resource-group {RESOURCE_GROUP_NAME} --sku {IOT_HUB_SKU} --verbose "
#        f"--partition-count {IOT_HUB_PARTITION_COUNT}"
#        )

#repeated?????????????????????


# TODO: use subprocess to parse json and give us a map of the deviceids and connections strings 
# direct_output = subprocess.check_output('ls', shell=True) #could be anything here.
for j in range(IOT_HUB_NUM_DEVICES):
    device_name = IOT_HUB_NAME[j]
    os.system(f"az iot hub device-identity create -n {IOT_HUB_NAME} "
            f"-d {device_name}"
            )

from azure.cli.core import get_default_cli
connec_string=[]

for j in range(IOT_HUB_NUM_DEVICES):
    device_name=str(IOT_HUB_NAME[j])
    connec_string[j]= get_default_cli().invoke(['iot', 'hub', 'show-connection-string', '--name',device_name])



# az extension add --name azure-iot
# az iot hub monitor-events --hub-name {IOT_HUB_NAME}