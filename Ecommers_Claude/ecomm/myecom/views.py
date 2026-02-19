from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, UpdateView
from django.db.models import Q, Min, Max
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Product, Category, Brand, Review, User
from .forms import UserRegistrationForm, LoginForm, UserProfileForm

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "myecom/dashboard/overview.html"

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "myecom/dashboard/profile.html"
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('profile_edit')

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)

from .models import Order, OrderItem, Wishlist, Address

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "myecom/dashboard/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "myecom/dashboard/order_detail.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = "myecom/dashboard/wishlist.html"
    context_object_name = "wishlist_items"
    paginate_by = 10

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = "myecom/dashboard/address_list.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.first_name}! Your account has been created.")
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'myecom/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'home')
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'myecom/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

class HomeView(TemplateView):
    template_name = "myecom/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(is_featured=True, is_active=True)[:8]
        context['trending_products'] = Product.objects.filter(is_trending=True, is_active=True)[:8]
        context['categories'] = Category.objects.filter(parent=None, is_active=True)[:6]
        return context

class ProductListView(ListView):
    model = Product
    template_name = "myecom/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | 
                Q(description__icontains=q) |
                Q(brand__name__icontains=q) |
                Q(category__name__icontains=q)
            )
            
        # Category Filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Brand Filter
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)

        # Price Filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)

        # Sorting
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('base_price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-base_price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'popularity':
            queryset = queryset.order_by('-view_count')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent=None, is_active=True)
        context['brands'] = Brand.objects.filter(is_active=True)
        # Price range for filter slider
        price_agg = Product.objects.filter(is_active=True).aggregate(min_p=Min('base_price'), max_p=Max('base_price'))
        context['min_price_range'] = price_agg['min_p']
        context['max_price_range'] = price_agg['max_p']
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = "myecom/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Related products (same category)
        context['related_products'] = Product.objects.filter(
            category=self.object.category, 
            is_active=True
        ).exclude(id=self.object.id)[:4]
        
        context['reviews'] = self.object.reviews.filter(is_approved=True)
        return context
