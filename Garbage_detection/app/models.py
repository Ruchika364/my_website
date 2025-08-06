from django.db import models

class GarbageDetection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('cleaned', 'Cleaned'),
    ]

    image = models.ImageField(upload_to='garbage_detections/')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    detections_today = models.DateTimeField(auto_now_add=True)
    verify= models.ImageField(upload_to='verification_images/', null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    address = models.CharField(max_length=500, blank=True, null=True) 

    def __str__(self):
        return f"Garbage at ({self.latitude}, {self.longitude}) - {self.status}"



from django.db import models

class VideoUpload(models.Model):
    video = models.FileField(upload_to='uploads/videos/')
    metadata_file = models.FileField(upload_to='uploads/metadata/')
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)