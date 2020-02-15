from django.urls import path, include

urlpatterns = [
    path('', include('image_slicer.urls')),
]
