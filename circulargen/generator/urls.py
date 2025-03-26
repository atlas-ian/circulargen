from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_circular, name='generate_circular'),
    path('send_whatsapp/', views.send_whatsapp, name='send_whatsapp'),

]
