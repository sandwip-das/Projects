from django.contrib import admin
from .models import (
    Category, Brand, Product, ProductImage, ProductVariant, 
    CustomerProfile, Address, Review, Wishlist, Coupon, 
    Order, OrderItem, Question
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'stock', 'category', 'brand', 'is_featured', 'is_trending')
    list_filter = ('category', 'brand', 'is_featured', 'is_trending')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline, ProductVariantInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')

# Register other models
admin.site.register(Brand)
admin.site.register(CustomerProfile)
admin.site.register(Address)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(Coupon)
admin.site.register(OrderItem)
admin.site.register(Question)
