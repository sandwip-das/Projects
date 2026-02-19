from django.urls import path
from .views import (
    HomeView, ProductListView, ProductDetailView, register_view, login_view, logout_view, 
    DashboardView, ProfileEditView, OrderListView, OrderDetailView, WishlistView, AddressListView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('shop/', ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    
    # Auth
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/profile/', ProfileEditView.as_view(), name='profile_edit'),
    path('dashboard/orders/', OrderListView.as_view(), name='order_list'),
    path('dashboard/orders/<str:order_number>/', OrderDetailView.as_view(), name='order_detail'),
    path('dashboard/wishlist/', WishlistView.as_view(), name='wishlist'),
    path('dashboard/addresses/', AddressListView.as_view(), name='address_list'),
]
