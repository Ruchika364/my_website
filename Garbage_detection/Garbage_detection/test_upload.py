import requests

# Replace with your current ngrok forwarding URL + endpoint path
url = 'https://6c228c1c901a.ngrok-free.app/upload/'  

# Replace with your actual test video file path
file_path = 'testvideo.mp4'

# Open the file in binary read mode
with open(file_path, 'rb') as f:
    files = {'video': f}
    response = requests.post(url, files=files)

# Print the response from your Django server
print("Status code:", response.status_code)
print("Response text:", response.text)
