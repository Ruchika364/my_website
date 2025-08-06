from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login
from django.shortcuts import render, get_object_or_404,redirect
from django.utils import timezone
from datetime import timedelta
from .models import GarbageDetection
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from ultralytics import YOLO
import cv2
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.contrib import messages
from .forms import GarbageDetectionForm
from django.views.decorators.csrf import csrf_exempt
import os
from django.db import models
import uuid
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import VideoUpload

# *************************************************

from django.shortcuts import render

def test_upload_page(request):
    return render(request, 'app/test_upload.html')


# *************************************************


#def my_login(request)
#def home_page(request)
# def map_location(request, detection_id)
# def detection_list(request)
# @csrf_exempt
# def update_status(request, detection_id)
#def is_admin(user):
# def is_viewer(user):
# def is_worker(user)
# @login_required
# @user_passes_test(is_admin)
# @login_required
# @user_passes_test(is_worker)
# @login_required
# def all_detections_view(request):

#--------------------------------------------MY_LOGIN-------------------------------------------------------------------------


def my_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
          
            return redirect('home_page')  # or your desired redirect
    else:
        form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})

#--------------------------------------------YOLO_MODEL--------------------------------------------------------------------------


model = YOLO('D:\\Website\\Garbage_detection_website\\Garbage_detection\\models\\best.pt')

#--------------------------------------------HOME_PAGE--------------------------------------------------------------------------

@login_required
def home_page(request):
    detection_count = 0 
    message = ''
    
    if request.method == 'POST' and request.FILES.get('video'):
        video = request.FILES['video']
        metadata_file = request.FILES.get('metadata')


         # ✅ Check that the file uploaded as video extention
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        ext = os.path.splitext(video.name)[1].lower()
        if ext not in valid_extensions:
             message = 'Invalid file type. Please upload a video file (.mp4, .avi, .mov, .mkv).'
             detections = GarbageDetection.objects.all().order_by('-detections_today')
             return render(request, 'app/home.html', {'message': message, 'detections': detections})
        
        #  To validate uploads securely (avoid users uploading malicious executables).
        #  When accepting uploads from untrusted users who can change filename virus.exe to video.mp4
        #This MIME checking will block those files by checking content of those files
        
        # Validate by MIME type
        if not video.content_type.startswith('video/'):
            message = 'Invalid file type. Please upload a valid video file.'
            detections = GarbageDetection.objects.all().order_by('-detections_today')
            return render(request, 'app/home.html', {'message': message, 'detections': detections})

        # Read metadata if provided
        latitude = None
        longitude = None

        location_data_by_frame = {}

        if metadata_file:
            try:
                metadata_json = json.load(metadata_file)
                # latitude = metadata_json.get('latitude')
                # longitude = metadata_json.get('longitude')

                for item in metadata_json.get('location_data', []):
                    frame_num = item.get('frame_number')
                    if frame_num is not None:
                        location_data_by_frame[frame_num] = {
                            'latitude': item.get('latitude'),
                            'longitude': item.get('longitude')
                        }   
            except Exception as e:
                print("Error parsing metadata:", e)

        
        fs = FileSystemStorage()
        filename = fs.save(video.name, video)
        video_path = fs.path(filename)
        cap = cv2.VideoCapture(video_path)

        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % 30 == 0:
            
                results = model(frame)
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        img_name = f'detection_frame_{uuid.uuid4()}.jpg'
                        save_path = os.path.join('media/detections', img_name)
                        cv2.imwrite(save_path, frame)

                        # Get GPS location for this frame (if available)
                        gps_info = location_data_by_frame.get(frame_count, {})
                        latitude = gps_info.get('latitude')
                        longitude = gps_info.get('longitude')

                        
                        GarbageDetection.objects.create(
                            image=f'detections/{img_name}',
                            latitude=latitude,
                            longitude=longitude,
                            detections_today=timezone.now().date(),
                            status='pending'
                            )
        cap.release()
        message = 'Video processed successfully'
    
    # Previous pending detections (before today, still pending)
    today = timezone.localtime().date()
    detections_today = GarbageDetection.objects.filter(
    detections_today__date=today
    ).order_by('-detections_today')

    previous_pending = GarbageDetection.objects.filter(
        ~Q(detections_today__date=today),
        status='pending'
    ).order_by('-detections_today')

    return render(request, 'app/home.html', {
    'message': message,
    'detections_today': detections_today,
    'previous_pending': previous_pending
})

#--------------------------------------------DELETE_CLEANED--------------------------------------------------------------------------



def delete_cleaned(request):
    if request.method == 'POST':
        deleted_count, _ = GarbageDetection.objects.filter(status='cleaned').delete()
        messages.success(request, f'{deleted_count} cleaned detections deleted successfully.')
        return redirect('home_page')




#--------------------------------------------MAP_LOCATION--------------------------------------------------------------------------

def map_location(request, detection_id):
    detection = get_object_or_404(GarbageDetection , id=detection_id)
     # ✅ Debug print

    return render(request, 'app/map_location2.html', {'detection': detection})




#--------------------------------------------DETECTION_LIST--------------------------------------------------------------------------


def detection_list(request):
    filter_type = request.GET.get('filter', 'all')
    detections = GarbageDetection.objects.all()

    now = timezone.now()

    if filter_type == 'today':
        detections = detections.filter(detections_today__date=now.date())
    elif filter_type == 'week':
        week_ago = now - timedelta(days=7)
        detections = detections.filter(detections_today__gte=week_ago)
    elif filter_type == 'month':
        month_ago = now - timedelta(days=30)
        detections = detections.filter(detections_today__gte=month_ago)

    detections = detections.order_by('-detections_today')

     # ✅ Handle image upload
    if request.method == 'POST':
        form = GarbageDetectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('detection_list')
    else:
        form = GarbageDetectionForm()
    return render(request, 'app/detection_list.html', {'detections': detections , 'form': form})





#--------------------------------------------DAILY_MAP--------------------------------------------------------------------------


def daily_map(request):
    today = timezone.now().date()
    detections = GarbageDetection.objects.filter(detections_today__date=today)
    return render(request, 'app/daily_map2.html', {'detections': detections})


    

#--------------------------------------------UPDATE_STATUS--------------------------------------------------------------------------



from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_status(request, detection_id):
    if request.method == 'POST':
        # ✅ Get status from form POST data
        status = request.POST.get('status')
        if status:
            detection = GarbageDetection.objects.get(id=detection_id)
            detection.status = status
            detection.save()
            # ✅ Redirect to detection_list page after update
            return HttpResponseRedirect(reverse('detection_list'))
        else:
            return JsonResponse({'error': 'No status provided'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


#--------------------------------------------IS_admin--------------------------------------------------------------------------



def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()


#--------------------------------------------IS_viewer-------------------------------------------------------------------------


def is_viewer(user):
    return user.groups.filter(name='Viewer').exists()


#--------------------------------------------IS_worker--------------------------------------------------------------------------


def is_worker(user):
    return user.groups.filter(name='Workers').exists()



#--------------------------------------------All_detection--------------------------------------------------------------------------


@login_required
def all_detections_view(request):
    # accessible to all logged in users
    detections = GarbageDetection.objects.all()
    return render(request, 'all_detections.html', {'detections': detections})


#----------------------------------------------UPLOAD---------------------------------------------------------------

# @csrf_exempt
# def upload_video(request):
    
#     print("Received request method:", request.method)

#     if request.method == "POST":
#         video = request.FILES.get('video')
#         metadata_str = request.POST.get('metadata')

#         if video:
#              # ✅ Generate a unique filename and save path
#             filename = f"{uuid.uuid4()}.mp4"
#             save_path = os.path.join(settings.MEDIA_ROOT, filename)

#             with open(save_path, 'wb+') as destination:
#                 for chunk in video.chunks():
#                     destination.write(chunk)
#             print("Saved to:", save_path) 

#             # ✅ Optional: save metadata as JSON file with same name
#             json_name = video_name.replace('.mp4', '.json')
#             json_path = os.path.join(settings.MEDIA_ROOT, json_name)
#             with open(json_path, 'w') as json_file:
#                 json.dump(metadata, json_file, indent=2)
#             print("Saved metadata to:", json_path)


#             return JsonResponse({"status": "success", "video_file": video_name, "metadata_file": json_name})
      
#     else:
#         return JsonResponse({"status": "failed", "reason": "Only POST allowed"})



@csrf_exempt
def upload_video(request):
    print("Received request method:", request.method)

    if request.method == "POST":
        video = request.FILES.get('video')
        metadata_file = request.FILES.get('metadata')  # file, not string

        if not video:
            return JsonResponse({"status": "failed", "reason": "No video file provided"})

        # Save video to uploads/videos/
        video_filename = f"{uuid.uuid4()}.mp4"
        video_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'videos', video_filename)
        os.makedirs(os.path.dirname(video_path), exist_ok=True)

        with open(video_path, 'wb+') as destination:
            for chunk in video.chunks():
                destination.write(chunk)

        print("Saved video to:", video_path)

        # Save metadata (if provided) to uploads/metadata/
        json_filename = None
        json_data = None 
        if metadata_file:
            try:
                json_data = json.load(metadata_file)
            except json.JSONDecodeError:
                return JsonResponse({"status": "failed", "reason": "Invalid JSON file"})

            json_filename = video_filename.replace('.mp4', '.json')
            json_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'metadata', json_filename)
            os.makedirs(os.path.dirname(json_path), exist_ok=True)

            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)

            print("Saved metadata to:", json_path)

        # ✅ Save to database
       
        data = {
            "video": f"uploads/videos/{video_filename}",
            "metadata_file": f"uploads/metadata/{json_filename}" if json_filename else None,
            "latitude": json_data.get("latitude") if json_data else None,
            "longitude": json_data.get("longitude") if json_data else None,
            "date": json_data.get("date") if json_data else None,
            "time": json_data.get("time") if json_data else None,
        }
          
        VideoUpload.objects.create(**data)
       
        return JsonResponse({
            "status": "success",
            "video_file": video_filename,
            "metadata_file": json_filename
        })

    return JsonResponse({"status": "failed", "reason": "Only POST method allowed"})


#-------------------------------------------UPLOAD IMAGE -----------------------------------------------------------

def upload_detection_image(request, pk):
    detection = get_object_or_404(GarbageDetection, pk=pk)
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            detection.verify = image
            detection.save()
    return redirect(request.META.get('HTTP_REFERER', 'detection_list'))



#-------------------------------------------UPLOAD HISTORY -----------------------------------------------------------


def upload_history(request):
    uploads = VideoUpload.objects.all().order_by('-id')  # newest first
    return render(request, 'app/upload_history.html', {'uploads': uploads})





#-------------------------------------------RUN_DETECTION -----------------------------------------------------------

@login_required
def run_detection(request, video_id):
    video_upload = get_object_or_404(VideoUpload, id=video_id)
    video_path = video_upload.video.path

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process 1 frame per second (assuming 30 FPS)
        if frame_count % 30 == 0:
            results = model(frame)
            for result in results:
                boxes = result.boxes
                if len(boxes):
                    img_name = f'detection_from_history_{frame_count}_{timezone.now().strftime("%Y%m%d%H%M%S")}.jpg'
                    save_path = os.path.join('media/detections', img_name)
                    cv2.imwrite(save_path, frame)
                    GarbageDetection.objects.create(
                        image=f'detections/{img_name}',
                        latitude=video_upload.latitude or 26.108109,
                        longitude=video_upload.longitude or 85.391409,
                        detections_today=timezone.now().date(),
                        status='pending'
                    )
                    saved = True
                    break

        frame_count += 1

        if saved:
            break

    cap.release()
    messages.success(request, "Detection run successfully.")
    return redirect('upload_history')

