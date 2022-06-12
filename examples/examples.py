import requests
import sys
from io import BytesIO

IMAGE_URLS = [
    'https://upload.wikimedia.org/wikipedia/commons/c/c8/Phalacrocorax_varius_-Waikawa%2C_Marlborough%2C_New_Zealand-8.jpg',
    'https://quiz.natureid.no/bird/db_media/eBook/679edc606d9a363f775dabf0497d31de8c3d7060.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/8/81/Eumomota_superciliosa.jpg',
    'https://i.pinimg.com/originals/f3/fb/92/f3fb92afce5ddff09a7370d90d021225.jpg',
    'https://cdn.britannica.com/77/189277-004-0A3BC3D4.jpg'
]

ENDPOINT = "http://localhost/predict"

def test_images(image_urls=IMAGE_URLS, endpoint=ENDPOINT):
    for image_url in image_urls:
        image_get_response = requests.get(image_url)
        image = BytesIO(image_get_response.content)
        res = requests.post(endpoint, files={"image": image})
        if res.status_code == 200:
            print(res.json())
        else:
            print(f"Error!\nImage: {image_url}\nReturned: {res.status_code}")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        test_images(endpoint=sys.argv[1])
    else:
        test_images()

