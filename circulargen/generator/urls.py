
from django.urls import path
from generator import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_circular/', views.generate_circular, name='generate_circular'),
    path('send-email/', views.send_email, name='send_email'),
    # path('send-email/', views.send_email, name='send_email'),

]
