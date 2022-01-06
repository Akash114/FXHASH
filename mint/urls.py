from django.urls import path, include
from . import  views

urlpatterns = [
    path('',views.index,name='mint'),
    path('mint_request',views.mint_request,name='mint_request')
]
