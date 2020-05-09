import random
import sys
from azure.iot.hub import IoTHubRegistryManager

# TODO: add env vars to prevent checking in secrets!
CONNECTION_STRING = "{IoTHubConnectionString}"
DEVICE_ID = "{deviceId}"

DEVICE_MESSAGE = "servo"
MESSAGE_COUNT = 1

def iothub_messaging_sample_run():
    try:
        # Create IoTHubRegistryManager
        registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

        for i in range(0, MESSAGE_COUNT):
            print ( 'Sending message: {0}'.format(i) )
            data = DEVICE_MESSAGE
            props={}
            # # optional: assign system properties
            # props.update(messageId = "message_%d" % i)
            # props.update(correlationId = "correlation_%d" % i)
            # props.update(contentType = "application/json")

            # optional: assign application properties
            # prop_text = "PropMsg_%d" % i
            # props.update(testProperty = prop_text)

            registry_manager.send_c2d_message(DEVICE_ID, data, properties=props)

        try:
            # Try Python 2.xx first
            raw_input("Press Enter to continue...\n")
        except:
            pass
            # Use Python 3.xx in the case of exception
            input("Press Enter to continue...\n")

    except Exception as ex:
        print ( "Unexpected error {0}" % ex )
        return
    except KeyboardInterrupt:
        print ( "IoT Hub C2D Messaging service sample stopped" )

if __name__ == '__main__':
    print ( "Starting the Python IoT Hub C2D Messaging service sample..." )

    iothub_messaging_sample_run()