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
    path('comment/<int:pk>/edit/', views.comment_edit, name='comment_edit'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('ajax/password-reset/', views.ajax_password_reset, name='ajax_password_reset'),
]
