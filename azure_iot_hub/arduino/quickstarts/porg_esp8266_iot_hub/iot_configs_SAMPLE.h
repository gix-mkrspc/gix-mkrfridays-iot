// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.


/*
*  USAGE: You must change this file from iot_configs_SAMPLE.h to iot_configs.h 
*  Also ensure this file is located in the same folder as the quickstart you're using (e.g blink_onboard_esp8266_iot_hub)
*  Please be sure NOT to check this file into source control as it contains credentials on your Wi-Fi and connection string for Azure IoT Hub
*
*  You must fill out the constants which have angle brackets in strings "<LIKE_THIS>"
*
*/

#ifndef IOT_CONFIGS_H
#define IOT_CONFIGS_H

/**
 * WiFi setup
 */
#define IOT_CONFIG_WIFI_SSID            "<YOUR_WIFI_SSID>"
#define IOT_CONFIG_WIFI_PASSWORD        "<YOUR_WIFI_PASSWORD>"

/**
 * IoT Hub Device Connection String setup
 * Find your Device Connection String by going to your Azure portal, creating (or navigating to) an IoT Hub, 
 * navigating to IoT Devices tab on the left, and creating (or selecting an existing) IoT Device. 
 * Then click on the named Device ID, and you will have able to copy the Primary or Secondary Device Connection String to this sample.
 */
#define DEVICE_CONNECTION_STRING    "<YOUR_DEVICE_CONNECTION_STRING>"

// The protocol you wish to use should be uncommented
//
#define SAMPLE_MQTT
//#define SAMPLE_HTTP

#endif /* IOT_CONFIGS_H */
