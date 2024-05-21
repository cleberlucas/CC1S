# Introduction
This project implements a facial recognition system for access control, using ESP32-CAM and ESP8266 devices. Identification information, including facial images and user data, is stored in a MySQL database. The system allows real-time facial recognition and entry permission management, suitable for environments such as offices, homes, and restricted facilities.

# Requirements
- Arduino IDE
- MySQL Server
- Operating System: Windows, Linux, or MacOS
- Python 3.7 (Best compatibility with the library)
- WiFi network (No internet connection required)
- Jumpers (13) for component connections
- ESP32-CAM and ESP8266 devices
- 220 OHMS resistors (4) for each individual LED
- Yellow LED (indicates a face was detected)
- Green LED (indicates a face was recognized)
- Red LED (indicates a face was not recognized)
- Blue LED (indicates access has been granted)

# Setup
Clone the Repository
Clone the repository to your local environment:
bash
Copiar código
```
git clone https://github.com/cleberlucas/CC1S/tree/domain/unifran
```
1. Database:
- Open the config.json file in server/.
- Configure/update the MySQL database connection with the appropriate credentials.
  
2. ESP Devices:
- Open the .ino files located in their respective folders using the Arduino IDE.
- Update the files with your WiFi network SSID and password.
- Upload the sketches to the devices.
- Connect the components of the ESP8266 according to Illustration 1.
- Connect both devices to a power source.
  
3. API:
- Run the app.py file located in server/api.
  
4. Facial Recognition
- Open the config.json file in server/ and configure/update the locations with the appropriate codes.
- Run the app.py file located in server/recognition.
  
# Notes
- Ensure to follow all installation and configuration steps correctly to guarantee the system operates properly.
- The entire ecosystem must be running on the same network.
- If you encounter issues during facial recognition, review the previous steps and check the connections and configurations of the ESP devices.
- Handle the ESP devices carefully and avoid connecting them while powered to prevent damage.
- If the system does not recognize the IP address of the devices via MAC, try manually connecting to the devices so the server can detect them.

# Future Implementations
- Alert for simultaneous entry of two people using presence sensors.
- Manual entry without facial confirmation. Note: The face will be recorded in the database as unknown for later audits.

# Endpoints Used in the Ecosystem
|                     ENDPOINT                        |     METHOD    |  PARAMETERS   | DESCRIPTION   |
| ----------------------------------------------------| ------------- | ------------- | ------------- |
<sub>esp32-url</sub>:81/stream| GET | NONE | Accesses video stream
<sub>esp-8266-url</sub>:88/led/<sub>yellow-blue-green-red</sub>/on  | GET |	NONE | Turn on the specified LED
<sub>esp-8266-url</sub>:88/led/<sub>yellow-blue-green-red</sub>/off | GET |	NONE | Turn off the specified LED
<sub>esp-8266-url</sub>:88/leds/on | GET |	NONE | Turns on all LEDs
<sub>esp-8266-url</sub>:88/leds/off |	GET |	NONE | Turns off all LEDs
http://localhost:5000/esp-32-cam | GET-POST-PUT | /{ID}, LOCATION, MAC | Manages the ESP32 camera
http://localhost:5000/esp-8266 | GET-POST |	LOCATION | Manages the ESP8266 device
http://localhost:5000/face | GET-POST |	LOCATION | Manages faces for facial recognition
http://localhost:5000/user | POST |	NONE | Creates a new user
http://localhost:5000/externals/unifran/user | POST | NONE | Creates a new user via external integration

## Illustration 1
![Captura de tela 2024-04-06 122711](https://github.com/cleberlucas/CC1S/assets/74572490/cc0f94a9-5377-4ca7-86a2-64c539dd2402)
