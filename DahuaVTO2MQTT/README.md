# DahuaVTO2MQTT
Listens to events from all Dahua devices - VTO, Camera, NVR unit and publishes them via MQTT Message

[Dahua VTO MQTT Events - examples](https://github.com/elad-bar/DahuaVTO2MQTT/blob/master/MQTTEvents.MD)

## How to install
### Docker Compose
```dockerfile
version: '2'
services:
  dahuavto2mqtt:
    image: "eladbar/dahuavto2mqtt:latest"
    container_name: "dahuavto2mqtt"
    hostname: "dahuavto2mqtt"
    restart: always
    environment:
      - DAHUA_VTO_HOST=vto-host
      - DAHUA_VTO_USERNAME=Username
      - DAHUA_VTO_PASSWORD=Password
      - MQTT_BROKER_HOST=mqtt-host
      - MQTT_BROKER_PORT=1883
      - MQTT_BROKER_USERNAME=Username
      - MQTT_BROKER_PASSWORD=Password 
      - MQTT_BROKER_TOPIC_PREFIX=DahuaVTO
      - MQTT_BROKER_CLIENT_ID=DahuaVTO2MQTT
      - DEBUG=False
```

### Environment Variables
| Variable                 | Default       | Required | Description                |
|--------------------------|---------------|----------|----------------------------|
| DAHUA_VTO_HOST           | -             | +        | Dahua VTO hostname or IP   |
| DAHUA_VTO_USERNAME       | -             | +        | Dahua VTO user name        |
| DAHUA_VTO_PASSWORD       | -             | +        | Dahua VTO password         |
| MQTT_BROKER_HOST         | -             | +        | MQTT Broker hostname or IP |
| MQTT_BROKER_PORT         | -             | +        | MQTT Broker port           |
| MQTT_BROKER_USERNAME     | -             | +        | MQTT Broker user name      |
| MQTT_BROKER_PASSWORD     | -             | +        | MQTT Broker password       |
| MQTT_BROKER_TOPIC_PREFIX | DahuaVTO      | -        | Topic to publish messages  |
| MQTT_BROKER_CLIENT_ID    | DahuaVTO2MQTT | -        | MQTT Broker client ID      |
| DEBUG                    | false         | -        | Enable debug log messages  |


## Commands

#### Open Door
By publishing MQTT message of {MQTT_BROKER_TOPIC_PREFIX}/Command/Open an HTTP request to the unit will be sent,
If the payload of the message is empty, default door to open is 1,
If unit supports more than 1 door, please add to the payload `Door` parameter with the number of the door 

## Changelog

* 2022-Jan-20 - MQTT Broker reconnect after 60 seconds

* 2022-Jan-07
  * Restructure code (2 clients - Dahua and MQTT)
  * Added support to mute call once ring using topic `DahuaVTO/Command/Mute`


* 2021-Dec-11
  
  * Changed MQTT Client to Mosquitto\Client
    
  * Use one connection with keep alive
    
  * Update MQTT Events


* 2020-Oct-21 - Reverted connection to per message, docker based image changed to php:7.4.11-cli


* 2020-Oct-12 - Added deviceType and serialNumber to MQTT message's payload, Improved connection to one time instead of per message


* 2020-Sep-04 - Edit Readme file, Added Supported Models and MQTT Events documentation


* 2020-Mar-27 - Added new environment variable - MQTT_BROKER_TOPIC_PREFIX


* 2020-Feb-03 - Initial version combing the event listener with MQTT


* 2021-Jan-01 - Ported to Python


* 2021-Jan-02 - MQTT Keep Alive, log level control via DEBUG env. variable


* 2021-Jan-15 - Fix [#19](https://github.com/elad-bar/DahuaVTO2MQTT/issues/19) - Reset connection after power failure or disconnection


* 2021-Jan-21
  * Added open door action when publishing an MQTT message with the topic - {MQTT_BROKER_TOPIC_PREFIX}/Command/Open
  
  * Reset connection when server sends EOF message gracefully instead of WARNING asyncio socket.send() raised exception


* 2021-04-22

  * Fix Invalid syntax in DahuaVTO.py line 117 [#41](https://github.com/elad-bar/DahuaVTO2MQTT/issues/41)

  * Added support for Door ID in DahuaVTO/Command/Open MQTT command [#29](https://github.com/elad-bar/DahuaVTO2MQTT/issues/29)


* 2021-04-23

  * Fix Open Door error

  
* 2021-04-24

  * Removed certificate verification when using SSL [#31](https://github.com/elad-bar/DahuaVTO2MQTT/issues/31)

  
* 2021-04-30

  * Changed MQTT message published log level to DEBUG
  * Fix DahuaVTOClient doesn't handle packets larger than Ethernet frame [#37](https://github.com/elad-bar/DahuaVTO2MQTT/issues/37)
  

* 2021-05-27
  
  * Added Lock State status to prevent duplicate attempts of unlock (which led to error log message since the unit didn't allow that operation)
  * Publish MQTT message with the lock status, more details in the [Dahua VTO MQTT Events - examples](https://github.com/elad-bar/DahuaVTO2MQTT/blob/master/MQTTEvents.MD) section
  * SSL support using new environment variable `DAHUA_VTO_SSL`

  
* 2021-05-28
  
  * All requests to Dahua unit are using socket (except open lock)


## Credits
All credits goes to <a href="https://github.com/riogrande75">@riogrande75</a> who wrote that complicated integration
Original code can be found in <a href="https://github.com/riogrande75/Dahua">@riogrande75/Dahua</a>
