from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('auto-suggest/', views.auto_suggest, name='auto_suggest'),
    path('product/<int:product_id>/question/', views.add_question, name='add_question'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # Compare
    path('compare/', views.compare_view, name='compare_view'),
    path('compare/add/<int:product_id>/', views.add_to_compare, name='add_to_compare'),
    path('compare/remove/<int:product_id>/', views.remove_from_compare, name='remove_from_compare'),
    path('compare/clear/', views.clear_compare, name='clear_compare'),
    
    # Invoice
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),

    # Supervisor
    path('supervisor/', views.supervisor_dashboard, name='supervisor_dashboard'),
    
    # Custom Admin
    path('custom-admin/', views.admin_dashboard, name='admin_dashboard'),
]
