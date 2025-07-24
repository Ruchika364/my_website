from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('map/<int:detection_id>/', views.map_location, name='map_location'),
    path('list/', views.detection_list, name='detection_list'),
    path('update_status/<int:detection_id>/', views.update_status, name='update_status'),
    path('daily_map2/', views.daily_map, name='daily_map'),
    path('login/', views.my_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('delete_cleaned/', views.delete_cleaned, name='delete_cleaned'),
    

    path('upload/', views.upload_video, name='upload'),
    path('upload_detection_image/<int:pk>/', views.upload_detection_image, name='upload_detection_image'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)