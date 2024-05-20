import requests

def create_esp_8266(mac_address, local):
    payload = {
        "mac": mac_address,
        "local": local
    }
    response = requests.post("http://localhost:5000/esp-8266", json=payload)

def create_esp_32_cam(mac_address, door, local, register_user_id):
    payload = {
        "mac": mac_address,
        "door": door,
        "local": local,
        "register_user_id": register_user_id
    }
    response = requests.post("http://localhost:5000/esp-32-cam", json=payload)

    return response.json()["id"]

def create_unifran_user(rgm, name, local, user_type):
    response = requests.post("http://localhost:5000/user", json={})
    user_id = response.json()["id"]

    payload = {
        "rgm": rgm,
        "user_id": user_id,
        "name": name,
        "local": local,
        "type": user_type
    }
    response = requests.post("http://localhost:5000/externals/unifran/user", json=payload)

    return user_id

def resgister_user(id, register_user_id):
    payload = {
        "register_user_id": register_user_id
    }

    response = requests.put(f"http://localhost:5000/esp-32-cam/{id}", json=payload)
    print(response.json())

#Example for use
create_esp_8266("48:55:19:EC:BF:4E", 69)
create_esp_32_cam('08:F9:E0:E3:E4:50', 'exit', 69, create_unifran_user(25136283, "Cleber", 69, "student"))
#resgister_user(1, null)