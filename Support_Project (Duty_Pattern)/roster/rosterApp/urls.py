from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('international/<int:year>/', views.international_roster, name='international_roster'),
    path('domestic/<int:year>/', views.domestic_roster, name='domestic_roster'),
]
