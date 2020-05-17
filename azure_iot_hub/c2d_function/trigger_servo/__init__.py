import logging
import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager

# Note that Azure Key Vault doesn't support underscores and some other special chars
# We substitute with a hyphen for underscore
CONNECTION_STRING = "{IoTHubConnectionString}"
DEVICE_ID = "{deviceId}"

DEVICE_MESSAGE = "servo"
MESSAGE_COUNT = 1

def iothub_messaging_sample_run():
    try:
        # Create IoTHubRegistryManager
        registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

        for i in range(0, MESSAGE_COUNT):
            logging.info ( 'Sending message: {0}'.format(i) )
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

        # try:
        #     # Try Python 2.xx first
        #     raw_input("Press Enter to continue...\n")
        # except:
        #     pass
        #     # Use Python 3.xx in the case of exception
        #     input("Press Enter to continue...\n")

    except Exception as ex:
        logging.info ( "Unexpected error {0}" % ex )
        return
    except KeyboardInterrupt:
        logging.info ( "IoT Hub C2D Messaging service sample stopped" )

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info('***NOW EXECUTING C2D***')
    iothub_messaging_sample_run()
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')
    
    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
