from locust import HttpUser, task, between
import requests
import random
from io import BytesIO

IMAGE_URLS = [
    {
        'id': 1,
        'domain': 'upload.wikipedia.org',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Phalacrocorax_varius_-Waikawa%2C_Marlborough%2C_New_Zealand-8.jpg'
    },
    {
        'id': 2,
        'domain': 'quiz.natureid.no',
        'url': 'https://quiz.natureid.no/bird/db_media/eBook/679edc606d9a363f775dabf0497d31de8c3d7060.jpg'
    },
    {
        'id': 3,
        'domain': 'upload.wikimedia.org',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/8/81/Eumomota_superciliosa.jpg'
    },
    {
        'id': 4,
        'domain': 'i.pinimg.com',
        'url': 'https://i.pinimg.com/originals/f3/fb/92/f3fb92afce5ddff09a7370d90d021225.jpg'
    },
    {
        'id': 5,
        'domain': 'cdn.britannica.com',
        'url': 'https://cdn.britannica.com/77/189277-004-0A3BC3D4.jpg'
    }
]


def pick_image():
    image_info = random.choice(IMAGE_URLS)
    image_id = image_info['id']
    image_domain = image_info['domain']
    image_url = image_info['url']
    image_get_response = requests.get(image_url)
    image = BytesIO(image_get_response.content)
    return image_id, image_domain, image_url, image


class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def hello_world(self):
        image_id, image_domain, image_url, image = pick_image()
        res = self.client.post("/predict", files={"image": image}, name=f"{image_id} - {image_domain}")
        if res.status_code == 200:
            print(res.json())
        else:
            print(f"Error!\nImage: {image_url}\nReturned: {res.status_code}")
