from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    User, SocialLogin, Address, Category, Brand, Product, ProductImage, 
    ProductVariant, ProductAttribute, Review, ReviewVote, ProductQuestion, ProductAnswer,
    Cart, CartItem, Wishlist, ProductComparison, ComparisonItem,
    Order, OrderItem, Payment, ReturnRefund, Coupon, ShippingZone
)

# Custom Admin Site for Supervisor/Superuser Control
class MyEcomAdminSite(admin.AdminSite):
    site_header = 'MyEcom Administration'
    site_title = 'MyEcom Admin'
    index_title = 'Dashboard Overview'

    def index(self, request, extra_context=None):
        # Add custom stats to the dashboard
        from django.db.models import Sum, Count
        extra_context = extra_context or {}
        extra_context['total_orders'] = Order.objects.count()
        extra_context['total_sales'] = Order.objects.filter(payment_status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        extra_context['total_users'] = User.objects.count()
        extra_context['low_stock_products'] = Product.objects.filter(stock_quantity__lte=10).count()
        return super().index(request, extra_context)

admin_site = MyEcomAdminSite(name='myecom_admin')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'country_of_origin', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price_display', 'stock_quantity', 'stock_status', 'is_active', 'image_preview')
    list_filter = ('is_active', 'stock_status', 'brand', 'category')
    search_fields = ('name', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    
    def price_display(self, obj):
        return f"{obj.base_price} {obj.currency}" if hasattr(obj, 'currency') else obj.base_price
    
    def image_preview(self, obj):
        if obj.images.exists():
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.images.first().image_url)
        return "No Image"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'order_status', 'payment_status', 'created_at')
    list_filter = ('order_status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__email', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')

    def order_number_display(self, obj):
        return obj.order_number # Assuming order_number exists

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_type', 'city', 'country')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

# Register other models to default admin as well
# User, Category, Brand, Product, Order, Address, Review are already registered via decorators


from .models import SiteConfiguration

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('site_name', 'site_description', 'logo', 'favicon')
        }),
        ('Contact Information', {
            'fields': ('support_phone', 'support_email', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url')
        }),
        ('Footer', {
            'fields': ('footer_text', 'copyright_text')
        }),
    )

    def has_add_permission(self, request):
        # Check if there's already an instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def changelist_view(self, request, extra_context=None):
        # Redirect to edit view if only one instance exists
        if self.model.objects.all().count() == 1:
            obj = self.model.objects.all()[0]
            return self.change_view(request, str(obj.pk))
        return super().changelist_view(request, extra_context)
