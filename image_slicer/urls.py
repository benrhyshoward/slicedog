from django.urls import path

from . import views

app_name = 'image_slicer'
urlpatterns = [
    path('', views.index_view, name='index'),
    path('<int:image_id>/', views.detail_view, name='detail'),
    path('<int:image_id>/sliced', views.sliced_view, name='sliced')
]