import requests

url = 'https://3ebb716a174f.ngrok-free.app/upload/'

file_path = 'D:\\garbage_for_website_3second.mp4'

with open(file_path, 'rb') as f:
    files = {'video': f}  # <-- change 'file' to 'video'
    response = requests.post(url, files=files)

print("Status code:", response.status_code)
print("Response text:", response.text)
