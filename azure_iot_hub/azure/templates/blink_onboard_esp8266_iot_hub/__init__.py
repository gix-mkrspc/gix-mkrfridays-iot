import logging
import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager

# Note that Azure Key Vault doesn't support underscores
#  and some other special chars;
#  we substitute with a hyphen for underscore
CONNECTION_STRING = "{c2d connection string}"
DEVICE_ID = "{device to invoke}"
MESSAGE_COUNT = 1


def iothub_messaging_sample_run(msg):
    try:
        #  IoTHubRegistryManager
        registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

        for i in range(0, MESSAGE_COUNT):
            logging.info('Sending message: {0}'.format(i))
            data = msg
            props = {}
            registry_manager.send_c2d_message(
                DEVICE_ID,
                data,
                properties=props)

    except Exception as ex:
        logging.info(f"Unexpected error {ex}")
        return


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    msg = "blink"
    logging.info('***NOW EXECUTING C2D***')
    iothub_messaging_sample_run(msg)
    return func.HttpResponse(
            f"The {msg} has been sent to the"
            " device successfully!")
