from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contact/', views.contact_us, name='contact_us'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.search, name='search'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    
    # Post Management URLs must come before post_detail
    path('post/new/', views.PostCreateView.as_view(), name='create_post'),
    path('post/<slug:slug>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    path('post/<slug:slug>/like/', views.post_interaction, name='post_interaction'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
]
