# Execution Order

1. Run the script `CREATE DATABASE With Schemas.sql` to create the necessary database with schemas.
2. Configure database access in `facialDataAccessLayer.py`.
3. Set the URL server, id and local on ESP32-CAM and ESP8266 ino files.
4. Run the script `facialRecogntionSys.py`.

**WARNING: ALL DEVICES MUST BE RUNNING ON THE SAME NETWORK**

# ESP8266 Commands

## Turning on/off individual LEDs:

### Yellow LED:

- On: `curl -X GET http://<ESP8266URL>/led/yellow/on`
- Off: `curl -X GET http://<ESP8266URL>/led/yellow/off`

### Green LED:

- On: `curl -X GET http://<ESP8266URL>/led/green/on`
- Off: `curl -X GET http://<ESP8266URL>/led/green/off`

### Red LED:

- On: `curl -X GET http://<ESP8266URL>/led/red/on`
- Off: `curl -X GET http://<ESP8266URL>/led/red/off`

### Blue LED:

- On: `curl -X GET http://<ESP8266URL>/led/blue/on`
- Off: `curl -X GET http://<ESP8266URL>/led/blue/off`

## Controlling all LEDs:

- Turn all LEDs on: `curl -X GET http://<ESP8266URL>/leds/on`
- Turn all LEDs off: `curl -X GET http://<ESP8266URL>/leds/off`
