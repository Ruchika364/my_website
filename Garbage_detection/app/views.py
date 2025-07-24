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

# ************************************************************************************
model = YOLO('D:\\Website\\Garbage_detection_website\\Garbage_detection\\models\\best.pt')

@login_required
def home_page(request):
    detection_count = 0 
    message = ''
    


    if request.method == 'POST' and request.FILES.get('video'):
        video = request.FILES['video']


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
                        img_name = f'detection_frame_{frame_count}_{timezone.now().strftime("%Y%m%d%H%M%S")}.jpg'
                        save_path = os.path.join('media/detections', img_name)
                        cv2.imwrite(save_path, frame)
                        latitude = 26.108109 + frame_count * 0.0001
                        longitude = 85.391409 + frame_count * 0.0001
                        GarbageDetection.objects.create(
                            image=f'detections/{img_name}',
                            latitude = 26.108109 + frame_count * 0.0001,
                            longitude = 85.391409 + frame_count * 0.0001, # Replace later
                            detections_today=timezone.now().date(),
                            status='pending'
                            )
        cap.release()
        message = 'Video processed successfully'
    

    
    

    # Previous pending detections (before today, still pending)
    today =today = timezone.localtime().date()
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




def delete_cleaned(request):
    if request.method == 'POST':
        deleted_count, _ = GarbageDetection.objects.filter(status='cleaned').delete()
        messages.success(request, f'{deleted_count} cleaned detections deleted successfully.')
        return redirect('home_page')



def map_location(request, detection_id):
    detection = get_object_or_404(GarbageDetection , id=detection_id)
     # ✅ Debug print

    return render(request, 'app/map_location2.html', {'detection': detection})



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




def daily_map(request):
    today = timezone.now().date()
    detections = GarbageDetection.objects.filter(detections_today__date=today)
    return render(request, 'app/daily_map2.html', {'detections': detections})





# @csrf_exempt
# def update_status(request, detection_id):
#     # print("req received");
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         status = data.get('status')
#         detection = GarbageDetection.objects.get(id=detection_id)
#         detection.status = status
#         detection.save()
#         return JsonResponse({'message': 'Status updated'})
#     else:
#         return JsonResponse({'error': 'Invalid request'}, status=400)
    




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





def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()



def is_viewer(user):
    return user.groups.filter(name='Viewer').exists()



def is_worker(user):
    return user.groups.filter(name='Workers').exists()





@login_required
def all_detections_view(request):
    # accessible to all logged in users
    detections = GarbageDetection.objects.all()
    return render(request, 'all_detections.html', {'detections': detections})






# from django.conf import settings

# from django.http import JsonResponse, HttpResponse




@csrf_exempt
def upload_video(request):
    if request.method == "POST":
        video = request.FILES.get('video')
        if video:
            with open('garbage_for_website_3second.mp4', 'wb+') as destination:
                for chunk in video.chunks():
                    destination.write(chunk)
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "failed", "reason": "No file provided"})
    else:
        return JsonResponse({"status": "failed", "reason": "Only POST allowed"})


def upload_detection_image(request, pk):
    detection = get_object_or_404(GarbageDetection, pk=pk)
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            detection.verify = image
            detection.save()
    return redirect(request.META.get('HTTP_REFERER', 'detection_list'))