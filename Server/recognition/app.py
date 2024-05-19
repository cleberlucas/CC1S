import asyncio
import json
import base64
import pickle
import cv2
import aiohttp
import requests
import numpy as np
from utils.network import get_ip_from_mac



_dic_frame = {}
_dic_ip = {}

_dic_cameras_macs = {}
_dic_locks_macs = {}

_dic_user_resgister_id = {}

_classifier_face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def get_connection(local):
    try:
        global _dic_ip
        global _dic_cameras_macs
        global _dic_locks_macs

        api_url_local_camera = f"http://localhost:5000/esp-32-cam?local={local}"
        api_url_local_lock = f"http://localhost:5000/esp-8266?local={local}"

        endpoints = [api_url_local_camera, api_url_local_lock]

        _dic_cameras_macs[local] = []
        _dic_locks_macs[local]  = []
        
        for api_url in endpoints:
            response = requests.get(api_url)
            if response.status_code != 200:
                raise Exception(f"get_connection: Error making request. Status code:", response.status_code)
            
            data = response.json()
            for item in data:
                mac = item.get("mac")
 
                if mac:
                    ip = get_ip_from_mac(mac)

                    if ip is None:
                        raise Exception(f"get_connection: Not found ip to mac {mac}", response.status_code)

                    _dic_ip[mac] = ip
                    _dic_user_resgister_id[mac] = None

                    if api_url == api_url_local_camera:            
                        _dic_cameras_macs[local].append(mac)
                    else:
                        _dic_locks_macs[local].append(mac)

                    print(f"get_connection: Ip found {ip} to mac {mac} found")

    except Exception as e:
        raise Exception(f"get_connection: Error making request:", e)

async def get_face_async(camera_local=None):
    try:
        api_url = "http://localhost:5000/face"
        if camera_local:
            api_url += f"?local={camera_local}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    print("get_face_async: Error making request. Status code:", response.status)
                    return []
                
                return await response.json()
    except Exception as e:
        print("get_face_async: Error making request:", e)
        return []
    
async def send_face_async(user_id, frame, x, y, w, h):
    try:
        api_url = f"http://localhost:5000/face"

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        registered_face = gray_frame[y:y+h, x:x+w]
        serialized_face = pickle.dumps(registered_face)

        serialized_face_base64 = base64.b64encode(serialized_face).decode('utf-8')

        payload = {
            'user_id': user_id,
            'face_img': serialized_face_base64
        }

        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, headers=headers) as response:
                if response.status != 200:
                    print("send_face_async: Error making request. Status code:", response.status)

    except Exception as e:
        print("send_face_async: Error making request:", e)

async def lock_async(lock_local, command):
    try:
        api_url = f"http://{_dic_ip[_dic_locks_macs[lock_local][0]]}:88/{command}"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    print("lock_async: Error making request. Status code:", response.status)
                    return
    except Exception as e:
        print("lock_async: Error making request:", e)

async def capture_handler_async(mac_address):
    print(f"capture_handler_async: Initialized for MAC address {mac_address}")

    global _dic_ip

    cap = cv2.VideoCapture(f'http://{_dic_ip[mac_address]}:81/stream')

    if not cap.isOpened():
        print(f"capture_handler_async: Error opening video capture for MAC address {mac_address}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"capture_handler_async: Error reading frame for MAC address {mac_address}")
            return
        
        _dic_frame[mac_address] = frame
        print(f"capture_handler_async: Executed for MAC address {mac_address}")
        await asyncio.sleep(0.1)

async def stream_video_handler_async(mac_address, rotate_video=False, mirror_video=False):
    print(f"stream_video_handler_async: Initialized for MAC address {mac_address}")

    global _dic_frame

    while True:
        frame = _dic_frame[mac_address]
        if frame is None or frame.size == 0:
            await asyncio.sleep(0.2)
            continue

        if rotate_video:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        faces = _classifier_face.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)

        if mirror_video:
            frame = cv2.flip(frame, 1)

        cv2.imshow("Video", frame)
        cv2.waitKey(1)

        await asyncio.sleep(0.1)

async def recognition_handler_async(lock_local, camera_mac_address, rotate_video=False):
    print(f"recognition_handler_async: Initialized for MAC address {camera_mac_address}")

    global _dic_frame
    global _dic_user_resgister_id

    last_state_face_detected = None
    while True:
        frame = _dic_frame[camera_mac_address].copy()

        if rotate_video:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        if frame is None or frame.size == 0:
            print(f"recognition_handler_async: Frame not detected for MAC address {camera_mac_address}")

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = _classifier_face.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            print(f"recognition_handler_async: No faces detecteds for MAC address {camera_mac_address}")

            if last_state_face_detected is None or last_state_face_detected:
                await lock_async(lock_local, "led/yellow/off")
                last_state_face_detected = False
        else:
            print(f"recognition_handler_async: Faces detecteds for MAC address {camera_mac_address}")

            if last_state_face_detected is None or not last_state_face_detected:
                await lock_async(lock_local, "led/yellow/on")
                last_state_face_detected = True
            
            for (x, y, w, h) in faces:              
                if not _dic_user_resgister_id[camera_mac_address] is None:
                    await register_async(lock_local, 1 ,frame, x, y, w, h)
                else:
                    current_face = gray_frame[y:y+h, x:x+w]

                    recognized = False
                    for face in await get_face_async(lock_local):
                        face_img = face.get('face_img')

                        if face_img is not None:
                            res = cv2.matchTemplate(current_face, pickle.loads(base64.b64decode(face_img)), cv2.TM_CCOEFF_NORMED)
                            _, max_val, _, _ = cv2.minMaxLoc(res)

                            if max_val > 0.7: 
                                recognized = True
                                break
                    
                    if recognized:
                        await recognized_async(lock_local)
                        await unlock_async(lock_local)
                    else:  
                        await unrecognized_async(lock_local)

            
        await asyncio.sleep(0.1)


async def register_async(lock_local, user_id, frame, x, y, w, h):
    await lock_async(lock_local, "led/green/on")
    await send_face_async(user_id, frame, x, y, w, h)
    await lock_async(lock_local, "led/green/off")

async def recognized_async(lock_local):
    await lock_async(lock_local, "led/green/on")
    await asyncio.sleep(1)
    await lock_async(lock_local, "led/green/off")

async def unrecognized_async(lock_local):
    await lock_async(lock_local, "led/red/on")
    await asyncio.sleep(1)
    await lock_async(lock_local, "led/red/off")

async def unlock_async(lock_local):
    await lock_async(lock_local, "leds/off")          
    await lock_async(lock_local,"led/blue/on")
    await asyncio.sleep(1)
    await lock_async(lock_local,"leds/off")

async def run_tasks_sync(): 
    with open('../config.json') as f:
        config_data = json.load(f)
        locals = config_data['locals']

    tasks = []
    for local in locals:
        get_connection(local)
        for camera_mac_address in _dic_cameras_macs[local]:
            tasks.append(capture_handler_async(camera_mac_address))
            tasks.append(recognition_handler_async(local, camera_mac_address, True))
            tasks.append(stream_video_handler_async(camera_mac_address, True, True))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run_tasks_sync())
