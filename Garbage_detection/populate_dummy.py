# import os
# import django
# import random

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Garbage_detection.settings")
# django.setup()

# from app.models import GarbageDetection

# lat_min = 26.08
# lat_max = 26.16
# lon_min = 85.35
# lon_max = 85.44

# for i in range(1, 101):
#     lat = round(random.uniform(lat_min, lat_max), 6)
#     lon = round(random.uniform(lon_min, lon_max), 6)
#     img_filename = f"garbage_detections/sample{i}.jpg"

#     GarbageDetection.objects.create(
#         image=img_filename,
#         latitude=lat,
#         longitude=lon,
#         status='pending'
#     )

# print("✅ Inserted 100 dummy garbage detection records.")

#--------------------------------------------------------------------------------------------------------------------------------
#THE BELOW SCRIPT DOESN'T HAVE DEPNDENCY ON IMAGE  FILE NAME OR FILE TYPE 

# import os
# import django
# import random

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Garbage_detection.settings")
# django.setup()

# from app.models import GarbageDetection

# # Define lat/lon bounds
# lat_min = 26.08
# lat_max = 26.16
# lon_min = 85.35
# lon_max = 85.44

# # Path to your garbage_detections folder inside MEDIA_ROOT
# from django.conf import settings
# image_dir = os.path.join(settings.MEDIA_ROOT, 'garbage_detections')

# # List all image files dynamically
# image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# # Shuffle to randomize selection (optional)
# random.shuffle(image_files)

# # Insert each image into DB
# for img_file in image_files:
#     lat = round(random.uniform(lat_min, lat_max), 6)
#     lon = round(random.uniform(lon_min, lon_max), 6)
    
#     GarbageDetection.objects.create(
#         image=f'garbage_detections/{img_file}',
#         latitude=lat,
#         longitude=lon,
#         status='pending'
#     )

# print(f"✅ Inserted {len(image_files)} dummy garbage detection records.")



# -------------------------------------------------------------------------------------------------

#NOTEEE 
#VERRRRRRRRRRRRYYYYYYYYYYYYYYY impoRTANT
#this script below is using geoencoding so ity will request api everytime and waste 

# 🔷 Why only 5 records now?

# Geocoding API calls are billed (even if within free tier, unnecessary calls consume quota).


import os
import django
import random
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Garbage_detection.settings")
django.setup()

from app.models import GarbageDetection

# Your Google API key
GOOGLE_API_KEY = "YOUR_API_KEY"

def get_address(lat, lon):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key=AIzaSyCdj4rf58uMjBm-MhlR692jq_1GnDcAJeY"
    response = requests.get(url)
    data = response.json()
    print(response)
    print(data)
    if data['status'] == 'OK':
        return data['results'][0]['formatted_address']
    else:
        return 'Unknown Address'

# Define lat/lon bounds
lat_min = 26.08
lat_max = 26.16
lon_min = 85.35
lon_max = 85.44

# Path to your garbage_detections folder inside MEDIA_ROOT
from django.conf import settings
image_dir = os.path.join(settings.MEDIA_ROOT, 'garbage_detections')

# List all image files dynamically
image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# Shuffle to randomize selection (optional)
random.shuffle(image_files)

# Insert only 5 images into DB with geocoded addresses
for img_file in image_files[:5]:
    lat = round(random.uniform(lat_min, lat_max), 6)
    lon = round(random.uniform(lon_min, lon_max), 6)
    
    address = get_address(lat, lon)

    GarbageDetection.objects.create(
        image=f'garbage_detections/{img_file}',
        latitude=lat,
        longitude=lon,
        status='pending',
        address=address
    )
    print(f"Inserted: {img_file} | {address}")

print(f"✅ Inserted {min(5, len(image_files))} dummy garbage detection records with geocoded addresses.")

