# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient

import os
import random
import subprocess

RESOURCE_GROUP_NAME = "iot-porg"
RESOURCE_GROUP_LOCATION = "centralus"


IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-iothub"
# TODO: This should be grabbing from a text file or other source so that we have
# idempotency/consistent runs
# IOT_HUB_NAME = f"{RESOURCE_GROUP_NAME}-{random.randint(1,100000):05}"

IOT_HUB_SKU = "F1" # free tier
IOT_HUB_PARTITION_COUNT = "2" # free tier

IOT_HUB_NUM_DEVICES = 3
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

# TODO: check if IoTHub exists already?
print('Checking az cli iot-hub extension...')
os.system('az extension add --name azure-iot')
print('Creating iot hub')
os.system(f"az iot hub create --name {IOT_HUB_NAME} "
        f"--resource-group {RESOURCE_GROUP_NAME} --sku {IOT_HUB_SKU} --verbose "
        f"--partition-count {IOT_HUB_PARTITION_COUNT}"
        )
# TODO: use subprocess
# direct_output = subprocess.check_output('ls', shell=True) #could be anything here.

# The return value is another ResourceGroup object with all the details of the
# new group. In this case the call is synchronous: the resource group has been
# provisioned by the time the call returns.

# Optional line to delete the resource group
#resource_client.resource_groups.delete("PythonSDKExample-ResourceGroup-rg")

# TODO: check that IOTHub exists before attempting to create a new one
os.system(f"az iot hub create --name {IOT_HUB_NAME} "
        f"--resource-group {RESOURCE_GROUP_NAME} --sku {IOT_HUB_SKU} --verbose "
        f"--partition-count {IOT_HUB_PARTITION_COUNT}"
        )

for i in range(IOT_HUB_NUM_DEVICES):
    device_name = f"{IOT_HUB_DEVICE_PREFIX}-{random.randint(1,100000):05}"
    os.system(f"az iot hub device-identity create -n {IOT_HUB_NAME} "
            f"-d {device_name}"
            )