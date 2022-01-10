from django.urls import path, include
from . import  views

urlpatterns = [
    path('',views.login,name='home'),
    path('mint',views.index,name='mint'),
    path('mint_request',views.mint_request,name='mint_request'),
    path('mint_multiple',views.mint_multiple,name='mint_multiple'),
    path('update_process',views.update_process,name='update_process')
]
