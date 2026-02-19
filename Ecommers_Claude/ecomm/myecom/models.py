"""
E-Commerce Application Models
Complete models for a full-featured e-commerce platform
"""

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify


# ==========================================
# CUSTOM USER MANAGER
# ==========================================

class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


# ==========================================
# ABSTRACT BASE MODELS
# ==========================================

class TimeStampedModel(models.Model):
    """Abstract model for tracking creation and update times"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Abstract model for soft deletion"""
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        self.deleted_at = None
        self.save()


# ==========================================
# USER MANAGEMENT
# ==========================================

class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, SoftDeleteModel):
    """Custom user model with extended fields"""
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    profile_image = models.URLField(max_length=500, null=True, blank=True)
    
    # Verification flags
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Account status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Financial
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    loyalty_points = models.IntegerField(default=0)
    
    # Security
    last_login = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    preferred_currency = models.CharField(max_length=10, default='BDT')
    timezone = models.CharField(max_length=50, null=True, blank=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class SocialLogin(TimeStampedModel):
    """Social authentication provider links"""
    
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('apple', 'Apple'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_logins')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    provider_user_id = models.CharField(max_length=255)
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    profile_data = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'social_logins'
        unique_together = [['provider', 'provider_user_id']]
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.provider}"


class Address(TimeStampedModel, SoftDeleteModel):
    """User addresses for shipping and billing"""
    
    ADDRESS_TYPE_CHOICES = [
        ('shipping', 'Shipping'),
        ('billing', 'Billing'),
        ('both', 'Both'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES)
    label = models.CharField(max_length=50, null=True, blank=True)  # Home, Office, etc.
    
    # Contact information
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    # Address details
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, db_index=True)
    postal_code = models.CharField(max_length=20, db_index=True)
    country = models.CharField(max_length=100, default='BD')
    
    # GPS coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Flags
    is_default_shipping = models.BooleanField(default=False)
    is_default_billing = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'addresses'
        verbose_name_plural = 'Addresses'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['city']),
            models.Index(fields=['postal_code']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.city}"


# ==========================================
# CATALOG MANAGEMENT
# ==========================================

class Category(TimeStampedModel, SoftDeleteModel):
    """Product categories with hierarchical structure"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    # Media
    image = models.URLField(max_length=500, null=True, blank=True)
    banner_image = models.URLField(max_length=500, null=True, blank=True)
    icon = models.URLField(max_length=500, null=True, blank=True)
    
    # Hierarchy
    level = models.IntegerField(default=0)
    path = models.CharField(max_length=500, null=True, blank=True)  # Materialized path
    display_order = models.IntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    meta_keywords = models.TextField(null=True, blank=True)
    
    # Flags
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Cache
    product_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(TimeStampedModel, SoftDeleteModel):
    """Product brands"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    logo = models.URLField(max_length=500, null=True, blank=True)
    banner_image = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    website_url = models.URLField(max_length=500, null=True, blank=True)
    country_of_origin = models.CharField(max_length=100, null=True, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    
    # Flags
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.IntegerField(default=0)
    
    # Cache
    product_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'brands'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(TimeStampedModel, SoftDeleteModel):
    """Main product model"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('none', 'No Discount'),
    ]
    
    STOCK_STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('backorder', 'Backorder'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    barcode = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    
    # Relationships
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_name='products')
    
    # Descriptions
    short_description = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    specifications = models.JSONField(null=True, blank=True)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # MSRP
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Discount
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_start_date = models.DateTimeField(null=True, blank=True)
    discount_end_date = models.DateTimeField(null=True, blank=True)
    
    # Tax
    tax_class = models.CharField(max_length=50, null=True, blank=True)
    
    # Inventory
    stock_quantity = models.IntegerField(default=0, db_index=True)
    low_stock_threshold = models.IntegerField(default=10)
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS_CHOICES)
    
    # Physical attributes
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)  # kg
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # cm
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)   # cm
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # cm
    
    # Media
    video_url = models.URLField(max_length=500, null=True, blank=True)
    video_provider = models.CharField(max_length=50, null=True, blank=True)  # youtube, vimeo
    
    # Order limits
    min_order_quantity = models.IntegerField(default=1)
    max_order_quantity = models.IntegerField(null=True, blank=True)
    
    # Delivery
    estimated_delivery_days_min = models.IntegerField(null=True, blank=True)
    estimated_delivery_days_max = models.IntegerField(null=True, blank=True)
    
    # Policies
    warranty_period = models.CharField(max_length=100, null=True, blank=True)
    return_period_days = models.IntegerField(default=7)
    
    # Shipping
    shipping_required = models.BooleanField(default=True)
    is_digital = models.BooleanField(default=False)
    download_url = models.URLField(max_length=500, null=True, blank=True)
    
    # Display flags
    is_trending = models.BooleanField(default=False, db_index=True)
    is_popular = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_new = models.BooleanField(default=False, db_index=True)
    is_on_sale = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_visible = models.BooleanField(default=True)
    
    # Statistics (cached)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'), db_index=True)
    total_reviews = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    wishlist_count = models.IntegerField(default=0)
    sold_count = models.IntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    meta_keywords = models.TextField(null=True, blank=True)
    search_keywords = models.TextField(null=True, blank=True)
    
    # Publishing
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_products')
    
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def final_price(self):
        """Calculate final price after discount"""
        if self.discount_type == 'percentage' and self.discount_value:
            return self.base_price - (self.base_price * self.discount_value / 100)
        elif self.discount_type == 'fixed' and self.discount_value:
            return self.base_price - self.discount_value
        return self.base_price


class ProductImage(TimeStampedModel):
    """Product images"""
    
    IMAGE_TYPE_CHOICES = [
        ('gallery', 'Gallery'),
        ('thumbnail', 'Thumbnail'),
        ('zoom', 'Zoom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500)
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True)
    alt_text = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    display_order = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES, default='gallery')
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['display_order']
        indexes = [
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - Image {self.display_order}"


class ProductVariant(TimeStampedModel):
    """Product variants (size, color, etc.)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    
    # Variant details
    variant_type = models.CharField(max_length=50)  # size, color, material, etc.
    variant_value = models.CharField(max_length=200)  # Large, Red, Cotton, etc.
    
    # Price & weight adjustments
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    weight_adjustment = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.00'))
    
    # Inventory
    stock_quantity = models.IntegerField(default=0)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    
    # Flags
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'product_variants'
        ordering = ['display_order']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.variant_type}: {self.variant_value}"


class ProductAttribute(TimeStampedModel):
    """Product attributes and specifications"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    attribute_group = models.CharField(max_length=100, null=True, blank=True)
    attribute_name = models.CharField(max_length=100)
    attribute_value = models.CharField(max_length=500)
    is_filterable = models.BooleanField(default=False)
    is_comparable = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'product_attributes'
        ordering = ['display_order']
        indexes = [
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute_name}: {self.attribute_value}"


# ==========================================
# REVIEWS & Q&A
# ==========================================

class Review(TimeStampedModel, SoftDeleteModel):
    """Product reviews"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    pros = models.TextField(null=True, blank=True)
    cons = models.TextField(null=True, blank=True)
    images = models.JSONField(null=True, blank=True)  # Array of image URLs
    
    # Verification
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False)
    
    # Engagement
    helpful_count = models.IntegerField(default=0)
    unhelpful_count = models.IntegerField(default=0)
    
    # Reply
    reply = models.TextField(null=True, blank=True)
    replied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='review_replies')
    replied_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'reviews'
        unique_together = [['user', 'product', 'order']]
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['user']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.product.name} ({self.rating}★)"


class ReviewVote(TimeStampedModel):
    """Helpful/Unhelpful votes on reviews"""
    
    VOTE_TYPE_CHOICES = [
        ('helpful', 'Helpful'),
        ('unhelpful', 'Unhelpful'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_votes')
    vote_type = models.CharField(max_length=20, choices=VOTE_TYPE_CHOICES)
    
    class Meta:
        db_table = 'review_votes'
        unique_together = [['review', 'user']]
        indexes = [
            models.Index(fields=['review']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.vote_type}"


class ProductQuestion(TimeStampedModel, SoftDeleteModel):
    """Customer questions about products"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    
    is_answered = models.BooleanField(default=False, db_index=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'product_questions'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['user']),
            models.Index(fields=['is_answered']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.product.name}"


class ProductAnswer(TimeStampedModel, SoftDeleteModel):
    """Answers to product questions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(ProductQuestion, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='answers')
    
    is_staff_answer = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    answer = models.TextField()
    helpful_count = models.IntegerField(default=0)
    unhelpful_count = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'product_answers'
        indexes = [
            models.Index(fields=['question']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Answer to: {self.question}"


# ==========================================
# CART & WISHLIST
# ==========================================

class Cart(TimeStampedModel):
    """Shopping cart"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_id = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='carts')
    
    # Totals (cached)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'carts'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        if self.user:
            return f"Cart - {self.user.email}"
        return f"Cart - Guest {self.session_id}"


class CartItem(TimeStampedModel):
    """Items in shopping cart"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    product_snapshot = models.JSONField(null=True, blank=True)  # Cache product data
    
    class Meta:
        db_table = 'cart_items'
        unique_together = [['cart', 'product', 'variant']]
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Wishlist(TimeStampedModel):
    """User wishlist"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='wishlist_items')
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_notified = models.BooleanField(default=False)
    notes = models.CharField(max_length=500, null=True, blank=True)
    
    class Meta:
        db_table = 'wishlists'
        unique_together = [['user', 'product', 'variant']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.product.name}"


class ProductComparison(TimeStampedModel):
    """Product comparison lists"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparison_lists')
    session_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = 'product_comparisons'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Comparison - {self.user.get_full_name() if self.user else self.session_id}"


class ComparisonItem(TimeStampedModel):
    """Items in comparison list"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comparison = models.ForeignKey(ProductComparison, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comparison_items')
    display_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'comparison_items'
        unique_together = [['comparison', 'product']]
        ordering = ['display_order']
        indexes = [
            models.Index(fields=['comparison']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.comparison} - {self.product.name}"


# ==========================================
# ORDERS
# ==========================================

class Order(TimeStampedModel, SoftDeleteModel):
    """Customer orders"""
    
    ORDER_TYPE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('pos', 'POS'),
    ]
    
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    FULFILLMENT_STATUS_CHOICES = [
        ('unfulfilled', 'Unfulfilled'),
        ('partial', 'Partial'),
        ('fulfilled', 'Fulfilled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Customer
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    guest_email = models.EmailField(null=True, blank=True)
    guest_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Order details
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, db_index=True)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, db_index=True)
    fulfillment_status = models.CharField(max_length=50, choices=FULFILLMENT_STATUS_CHOICES)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    wallet_amount_used = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='BDT')
    
    # Addresses (stored as JSON snapshots)
    shipping_address_snapshot = models.JSONField()
    billing_address_snapshot = models.JSONField()
    
    # Notes
    customer_note = models.TextField(null=True, blank=True)
    admin_note = models.TextField(null=True, blank=True)
    
    # Shipping
    tracking_number = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    courier_name = models.CharField(max_length=100, null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Delivery verification
    delivery_otp = models.CharField(max_length=10, null=True, blank=True)
    delivery_signature_url = models.URLField(max_length=500, null=True, blank=True)
    delivered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivered_orders')
    
    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)  # web, mobile, app
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_orders')
    cancellation_reason = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user']),
            models.Index(fields=['order_status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['tracking_number']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'order_status']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"


class OrderItem(TimeStampedModel):
    """Items in an order"""
    
    RETURN_STATUS_CHOICES = [
        ('none', 'None'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, related_name='order_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.RESTRICT, null=True, blank=True, related_name='order_items')
    
    # Product snapshot (in case product is deleted/modified)
    product_snapshot = models.JSONField()
    product_name = models.CharField(max_length=500)
    sku = models.CharField(max_length=100)
    
    # Pricing
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Cost & profit
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Returns
    return_status = models.CharField(max_length=50, choices=RETURN_STATUS_CHOICES, null=True, blank=True)
    return_quantity = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'order_items'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class OrderStatusHistory(TimeStampedModel):
    """Order status change history"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=50, null=True, blank=True)
    to_status = models.CharField(max_length=50)
    notes = models.TextField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_status_updates')
    
    class Meta:
        db_table = 'order_status_history'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number}: {self.from_status} → {self.to_status}"


# ==========================================
# PAYMENTS
# ==========================================

class Payment(TimeStampedModel):
    """Payment transactions"""
    
    PAYMENT_METHOD_CHOICES = [
        ('sslcommerz', 'SSLCommerz'),
        ('cod', 'Cash on Delivery'),
        ('wallet', 'Wallet'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_number = models.CharField(max_length=50, unique=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='BDT')
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, db_index=True)
    
    # Gateway response
    gateway_response = models.JSONField(null=True, blank=True)
    
    # Card details (if applicable)
    card_last_four = models.CharField(max_length=4, null=True, blank=True)
    card_brand = models.CharField(max_length=50, null=True, blank=True)
    bank_transaction_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Timestamps
    paid_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Refund
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    refund_reason = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Payment #{self.payment_number} - {self.order.order_number}"


class SavedPaymentMethod(TimeStampedModel):
    """Saved payment methods for users"""
    
    PAYMENT_TYPE_CHOICES = [
        ('card', 'Card'),
        ('bank_account', 'Bank Account'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_payment_methods')
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES)
    provider = models.CharField(max_length=100)
    token = models.CharField(max_length=255)  # Encrypted token
    
    # Card details
    card_brand = models.CharField(max_length=50, null=True, blank=True)
    last_four = models.CharField(max_length=4, null=True, blank=True)
    expiry_month = models.IntegerField(null=True, blank=True)
    expiry_year = models.IntegerField(null=True, blank=True)
    cardholder_name = models.CharField(max_length=200, null=True, blank=True)
    
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_methods')
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'saved_payment_methods'
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.card_brand} ****{self.last_four}"


# ==========================================
# RETURNS & REFUNDS
# ==========================================

class ReturnRefund(TimeStampedModel):
    """Return and refund requests"""
    
    REQUEST_TYPE_CHOICES = [
        ('return', 'Return'),
        ('refund', 'Refund'),
        ('exchange', 'Exchange'),
    ]
    
    REASON_CATEGORY_CHOICES = [
        ('defective', 'Defective'),
        ('wrong_item', 'Wrong Item'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    REFUND_METHOD_CHOICES = [
        ('original_payment', 'Original Payment Method'),
        ('wallet', 'Wallet'),
        ('bank', 'Bank Transfer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    return_number = models.CharField(max_length=50, unique=True, db_index=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='returns')
    
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    reason_category = models.CharField(max_length=50, choices=REASON_CATEGORY_CHOICES)
    reason_detail = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True)
    
    # Refund details
    refund_method = models.CharField(max_length=50, choices=REFUND_METHOD_CHOICES, null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipping_cost_refunded = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    restocking_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Evidence
    images = models.JSONField(null=True, blank=True)  # Array of image URLs
    
    # Admin handling
    admin_notes = models.TextField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_returns')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_returns')
    rejected_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'return_refunds'
        indexes = [
            models.Index(fields=['return_number']),
            models.Index(fields=['order']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Return #{self.return_number} - Order {self.order.order_number}"


class ReturnRefundItem(models.Model):
    """Items included in return/refund request"""
    
    CONDITION_CHOICES = [
        ('unopened', 'Unopened'),
        ('opened', 'Opened'),
        ('damaged', 'Damaged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    return_refund = models.ForeignKey(ReturnRefund, on_delete=models.CASCADE, related_name='items')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='return_items')
    quantity = models.IntegerField()
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'return_refund_items'
        indexes = [
            models.Index(fields=['return_refund']),
            models.Index(fields=['order_item']),
        ]
    
    def __str__(self):
        return f"{self.order_item.product_name} x {self.quantity}"


# ==========================================
# MARKETING & PROMOTIONS
# ==========================================

class Coupon(TimeStampedModel, SoftDeleteModel):
    """Discount coupons"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    ]
    
    APPLICABLE_TO_CHOICES = [
        ('all', 'All Products'),
        ('categories', 'Specific Categories'),
        ('products', 'Specific Products'),
        ('brands', 'Specific Brands'),
        ('users', 'Specific Users'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    # Discount details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Conditions
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Applicability
    applicable_to = models.CharField(max_length=50, choices=APPLICABLE_TO_CHOICES, default='all')
    applicable_ids = models.JSONField(null=True, blank=True)  # Array of IDs
    exclude_sale_items = models.BooleanField(default=False)
    
    # Usage limits
    usage_limit_total = models.IntegerField(null=True, blank=True)
    usage_limit_per_user = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    first_order_only = models.BooleanField(default=False)
    
    # Validity
    valid_from = models.DateTimeField(db_index=True)
    valid_until = models.DateTimeField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_coupons')
    
    class Meta:
        db_table = 'coupons'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['valid_from']),
            models.Index(fields=['valid_until']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class CouponUsage(TimeStampedModel):
    """Coupon usage tracking"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='coupon_usages')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'coupon_usage'
        indexes = [
            models.Index(fields=['coupon']),
            models.Index(fields=['user']),
            models.Index(fields=['order']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.coupon.code} - {self.user.email}"


# ==========================================
# WALLET
# ==========================================

class WalletTransaction(TimeStampedModel):
    """Wallet transactions"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('refund', 'Refund'),
        ('cashback', 'Cashback'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions')
    transaction_number = models.CharField(max_length=50, unique=True)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_before = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Reference
    reference_type = models.CharField(max_length=50, null=True, blank=True)
    reference_id = models.UUIDField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='completed')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_wallet_transactions')
    
    class Meta:
        db_table = 'wallet_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_number} - {self.transaction_type}"


# ==========================================
# NOTIFICATIONS & ALERTS
# ==========================================

class Notification(TimeStampedModel):
    """User notifications"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('order', 'Order'),
        ('price_drop', 'Price Drop'),
        ('stock', 'Stock'),
        ('promotion', 'Promotion'),
        ('account', 'Account'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ]
    
    CHANNEL_CHOICES = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(null=True, blank=True)
    
    action_url = models.URLField(max_length=500, null=True, blank=True)
    action_text = models.CharField(max_length=100, null=True, blank=True)
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


class PriceDropAlert(TimeStampedModel):
    """Price drop alerts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_drop_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_drop_alerts')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='price_drop_alerts')
    
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    notification_methods = models.JSONField()  # ['email', 'sms', 'push']
    
    is_triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        db_table = 'price_drop_alerts'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


class BackInStockAlert(TimeStampedModel):
    """Back in stock alerts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_alerts')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='stock_alerts')
    
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    notification_methods = models.JSONField()  # ['email', 'sms', 'push']
    
    is_notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        db_table = 'back_in_stock_alerts'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


# ==========================================
# SHIPPING & TAX
# ==========================================

class ShippingZone(TimeStampedModel):
    """Shipping zones and rates"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    # Geographic coverage
    countries = models.JSONField()  # Array of country codes
    states = models.JSONField(null=True, blank=True)  # Array of state codes
    cities = models.JSONField(null=True, blank=True)  # Array of city names
    postal_codes = models.JSONField(null=True, blank=True)  # Array of postal codes
    postal_code_patterns = models.JSONField(null=True, blank=True)  # Regex patterns
    
    # Rates
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    per_kg_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Delivery estimates
    min_delivery_days = models.IntegerField(null=True, blank=True)
    max_delivery_days = models.IntegerField(null=True, blank=True)
    
    # COD
    is_cod_available = models.BooleanField(default=True)
    cod_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'shipping_zones'
        ordering = ['display_order']
    
    def __str__(self):
        return self.name


class Tax(TimeStampedModel):
    """Tax rates"""
    
    TAX_TYPE_CHOICES = [
        ('vat', 'VAT'),
        ('gst', 'GST'),
        ('sales_tax', 'Sales Tax'),
    ]
    
    APPLIES_TO_CHOICES = [
        ('all', 'All Products'),
        ('physical', 'Physical Products'),
        ('digital', 'Digital Products'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    tax_type = models.CharField(max_length=20, choices=TAX_TYPE_CHOICES)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Geographic scope
    country = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    state = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    
    # Applicability
    applies_to = models.CharField(max_length=20, choices=APPLIES_TO_CHOICES, default='all')
    priority = models.IntegerField(default=0)
    is_compound = models.BooleanField(default=False)  # Tax on tax
    is_inclusive = models.BooleanField(default=False)  # Included in price
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        db_table = 'taxes'
        ordering = ['priority']
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['state']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.rate}%)"


# ==========================================
# ACCESS CONTROL
# ==========================================

class Role(TimeStampedModel):
    """User roles"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    level = models.IntegerField(default=0)  # Hierarchy level
    is_system = models.BooleanField(default=False)  # Cannot be deleted
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'roles'
        ordering = ['level', 'name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class Permission(TimeStampedModel):
    """System permissions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True, db_index=True)
    module = models.CharField(max_length=100, db_index=True)  # products, orders, users, etc.
    description = models.TextField(null=True, blank=True)
    is_system = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'permissions'
        ordering = ['module', 'name']
        indexes = [
            models.Index(fields=['codename']),
            models.Index(fields=['module']),
        ]
    
    def __str__(self):
        return f"{self.module}.{self.codename}"


class RolePermission(TimeStampedModel):
    """Role-Permission mapping"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    
    class Meta:
        db_table = 'role_permissions'
        unique_together = [['role', 'permission']]
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['permission']),
        ]
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.codename}"


class UserRole(TimeStampedModel):
    """User-Role mapping"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_roles'
        unique_together = [['user', 'role']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


# ==========================================
# SUPPORT
# ==========================================

class SupportTicket(TimeStampedModel):
    """Customer support tickets"""
    
    CATEGORY_CHOICES = [
        ('order', 'Order'),
        ('product', 'Product'),
        ('payment', 'Payment'),
        ('account', 'Account'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting for Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_tickets')
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Metrics
    first_response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Satisfaction
    satisfaction_rating = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    satisfaction_comment = models.TextField(null=True, blank=True)
    
    tags = models.JSONField(null=True, blank=True)  # Array of tags
    
    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['user']),
            models.Index(fields=['order']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.subject}"


class SupportMessage(TimeStampedModel):
    """Messages in support tickets"""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('note', 'Internal Note'),
        ('system', 'System Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_messages')
    message = models.TextField()
    attachments = models.JSONField(null=True, blank=True)  # Array of file URLs
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    is_staff_reply = models.BooleanField(default=False)
    is_internal_note = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'support_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['ticket']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Message on {self.ticket.ticket_number}"


# ==========================================
# INVOICING
# ==========================================

class Invoice(TimeStampedModel):
    """Order invoices"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    invoice_date = models.DateTimeField()
    due_date = models.DateTimeField(null=True, blank=True)
    pdf_url = models.URLField(max_length=500, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    terms_conditions = models.TextField(null=True, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_invoices')
    
    class Meta:
        db_table = 'invoices'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['invoice_number']),
        ]
    
    def __str__(self):
        return f"Invoice #{self.invoice_number}"


# ==========================================
# EMAIL & LOGGING
# ==========================================

class EmailTemplate(TimeStampedModel):
    """Email templates"""
    
    CATEGORY_CHOICES = [
        ('transactional', 'Transactional'),
        ('marketing', 'Marketing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    subject = models.CharField(max_length=255)
    body_html = models.TextField()
    body_text = models.TextField(null=True, blank=True)
    variables = models.JSONField(null=True, blank=True)  # Available template variables
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'email_templates'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.name


class EmailLog(TimeStampedModel):
    """Email sending log"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='email_logs')
    to_email = models.EmailField(db_index=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='email_logs')
    subject = models.CharField(max_length=255)
    body = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'email_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['to_email']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.to_email} - {self.subject}"


class ActivityLog(TimeStampedModel):
    """System activity log"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action = models.CharField(max_length=100, db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.UUIDField(null=True, blank=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)  # Before/after data
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['entity_type']),
            models.Index(fields=['entity_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.entity_type}"


# ==========================================
# SYSTEM SETTINGS
# ==========================================

class SystemSetting(TimeStampedModel):
    """System configuration settings"""
    
    VALUE_TYPE_CHOICES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ]
    
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('payment', 'Payment'),
        ('shipping', 'Shipping'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('tax', 'Tax'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField(null=True, blank=True)
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=False)  # Can be accessed by frontend
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_settings')
    
    class Meta:
        db_table = 'system_settings'
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.key} = {self.value}"


# ==========================================
# ANALYTICS
# ==========================================

class SearchHistory(TimeStampedModel):
    """Search query tracking"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='search_history')
    session_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    search_query = models.CharField(max_length=500, db_index=True)
    filters_applied = models.JSONField(null=True, blank=True)
    results_count = models.IntegerField(default=0)
    clicked_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='search_clicks')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'search_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
            models.Index(fields=['search_query']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.search_query} ({self.results_count} results)"


class ProductViewLog(TimeStampedModel):
    """Product view tracking"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_views')
    session_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='view_logs')
    referrer_url = models.URLField(max_length=1000, null=True, blank=True)
    view_duration_seconds = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    
    class Meta:
        db_table = 'product_view_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
            models.Index(fields=['product']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.product.name} viewed"


class SiteConfiguration(TimeStampedModel):
    """Model for storing site-wide configuration settings"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site_name = models.CharField(max_length=255, default="SANDWIPS")
    site_description = models.TextField(blank=True, default="The largest retail chain of computer shops in Bangladesh.")
    
    # Contact Info
    support_phone = models.CharField(max_length=20, default="+880 1234 567 890")
    support_email = models.EmailField(default="support@sandwips.com")
    address = models.TextField(blank=True, default="Kusholi Bhaban, Agargaon, Dhaka-1207")
    
    # Social Media
    facebook_url = models.URLField(blank=True, default="#")
    twitter_url = models.URLField(blank=True, default="#")
    instagram_url = models.URLField(blank=True, default="#")
    linkedin_url = models.URLField(blank=True, default="#")
    youtube_url = models.URLField(blank=True, default="#")
    
    # Appearance
    # logo = models.ImageField(upload_to='site/', null=True, blank=True)
    # favicon = models.ImageField(upload_to='site/', null=True, blank=True)
    
    # Footer
    footer_text = models.TextField(blank=True, help_text="Text to display in the footer bottom")
    copyright_text = models.CharField(max_length=255, default="© 2026 Sandwips E-Shop. All rights reserved.")
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return "Site Configuration"
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteConfiguration.objects.exists():
            # If already exists, return the existing one
            return
        return super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(defaults={'site_name': "SANDWIPS"})
        return obj