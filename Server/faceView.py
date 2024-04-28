import requests
import numpy as np
import cv2

def visualize_faces_from_api(local=None):
    try:
        api_url = 'http://192.168.15.102:5000/face'
        params = {'local': local} if local else {}
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            faces = data['faces']

            for face in faces:
                name = face['name']
                user_id = face['user_id']
                face_img_data = face['face_img']

                registered_face = np.array(face_img_data, dtype=np.uint8)

                cv2.imshow(f'Face de {name} (ID: {user_id})', registered_face)
                cv2.waitKey(0)

            cv2.destroyAllWindows()

        else:
            print(f"Erro ao obter faces da API: {response.json()}")

    except Exception as e:
        print("Erro ao processar requisição:", str(e))

visualize_faces_from_api()
