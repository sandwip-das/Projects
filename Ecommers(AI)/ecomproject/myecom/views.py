from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min, Max, Avg, Sum
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, Category, Brand, Review, Order, OrderItem, Address, Wishlist, Coupon, Question, CustomerProfile
from .forms import UserRegistrationForm, LoginForm, CheckoutForm, ReviewForm, QuestionForm, ProfileForm, UserUpdateForm
from django.core.paginator import Paginator

# --- Home & Shop ---

def home(request):
    featured = Product.objects.filter(is_featured=True).annotate(avg_rating=Avg('reviews__rating'))[:8]
    trending = Product.objects.filter(is_trending=True).annotate(avg_rating=Avg('reviews__rating'))[:8]
    new_arrivals = Product.objects.order_by('-created_at').annotate(avg_rating=Avg('reviews__rating'))[:8]
    categories = Category.objects.filter(parent=None)  # Top level categories
    
    context = {
        'featured': featured,
        'trending': trending,
        'new_arrivals': new_arrivals,
        'categories': categories,
    }
    return render(request, 'home.html', context)

def shop(request):
    products = Product.objects.all().annotate(avg_rating=Avg('reviews__rating'))
    categories = Category.objects.filter(parent=None)
    brands = Brand.objects.all()
    
    # Filters
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        # Include children categories
        categories_ids = [category.id] + [c.id for c in category.children.all()]
        products = products.filter(category__id__in=categories_ids)

    brand_slug = request.GET.get('brand')
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)

    price_min = request.GET.get('min_price')
    price_max = request.GET.get('max_price')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    rating_filter = request.GET.get('rating')
    if rating_filter:
        products = products.filter(avg_rating__gte=rating_filter)

    stock_filter = request.GET.get('stock')
    if stock_filter == 'in_stock':
        products = products.filter(stock__gt=0)
        
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'shop.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    reviews = product.reviews.all().order_by('-created_at')
    
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    })

# --- Cart ---
def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, item_data in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = float(product.price) * item_data['quantity']
        total_price += subtotal
        cart_items.append({
            'product': product,
            'quantity': item_data['quantity'],
            'subtotal': subtotal
        })
    
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {'quantity': quantity}
    
    request.session['cart'] = cart
    messages.success(request, "Item added to cart")
    return redirect('cart_detail')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart_detail')

def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            if quantity > 0:
                cart[str(product_id)]['quantity'] = quantity
            else:
                del cart[str(product_id)]
            request.session['cart'] = cart
    return redirect('cart_detail')

# --- Checkout ---
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            now = timezone.now()
            coupon = Coupon.objects.get(code=code, active=True, valid_from__lte=now, valid_to__gte=now)
            request.session['coupon_id'] = coupon.id
            messages.success(request, "Coupon applied successfully!")
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
            messages.error(request, "Invalid or expired coupon code.")
    return redirect('checkout')

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('shop')
        
    total_price = 0
    items_to_create = []
    
    # Calculate total and prepare items
    for pid, data in cart.items():
        product = Product.objects.get(id=pid)
        total_price += float(product.price) * data['quantity']
        items_to_create.append((product, data['quantity'], product.price))

    # Apply Coupon
    coupon_id = request.session.get('coupon_id')
    discount_amount = 0
    coupon = None
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            if coupon.is_percentage:
                discount_amount = total_price * (float(coupon.discount) / 100)
            else:
                discount_amount = float(coupon.discount)
        except Coupon.DoesNotExist:
            del request.session['coupon_id']
    
    final_total = total_price - discount_amount

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            user = request.user
            if not user.is_authenticated:
                email = request.POST.get('email')
                # Simple guest logic: Try to find user or create one
                if not email:
                    messages.error(request, "Email is required for guest checkout.")
                    return redirect('checkout')
                
                try:
                    user = User.objects.get(email=email)
                    # If user exists, we associate order with them, but maybe they should have logged in?
                    # For this implementation, we allow it.
                except User.DoesNotExist:
                    import uuid
                    password = str(uuid.uuid4())
                    username = email.split('@')[0] + "_" + str(uuid.uuid4())[:4]
                    user = User.objects.create_user(username=username, email=email, password=password)
                    login(request, user) # Auto-login new guest user

            # Create Address
            address = form.save(commit=False)
            address.user = user
            address.save()
            
            # Create Order
            order = Order.objects.create(
                user=user,
                total_amount=final_total,
                shipping_address=address,
                billing_address=address, # Simplified
                coupon=coupon
            )
            
            # Create Order Items
            for product, qty, price in items_to_create:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=price
                )
            
            # Clear cart and coupon
            del request.session['cart']
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
                
            messages.success(request, "Order placed successfully!")
            return redirect('dashboard')
    else:
        form = CheckoutForm()
        
    return render(request, 'checkout.html', {
        'form': form, 
        'total_price': total_price, 
        'discount_amount': discount_amount,
        'final_total': final_total,
        'cart_items': items_to_create,
        'coupon': coupon
    })

# --- User Dashboard ---
@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    try:
        profile = request.user.profile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile.objects.create(user=request.user)
        
    return render(request, 'dashboard.html', {'orders': orders, 'profile': profile})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.select_related('shipping_address').prefetch_related('items__product'), id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

# --- Auth ---
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            CustomerProfile.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def auto_suggest(request):
    query = request.GET.get('q', '')
    data = []
    if query:
        products = Product.objects.filter(title__icontains=query)[:5]
        for p in products:
            data.append({'title': p.title, 'slug': p.slug, 'image': p.image.url if p.image else None, 'price': str(p.price)})
    return JsonResponse(data, safe=False)

@login_required
def add_question(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.product = product
            question.save()
            messages.success(request, "Question submitted successfully!")
        else:
            messages.error(request, "Error submitting question.")
    return redirect('product_detail', slug=product.slug)

# --- Wishlist ---
@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'dashboard.html', {'wishlist_items': wishlist_items, 'active_tab': 'wishlist'})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"{product.title} added to wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"{product.title} removed from wishlist.")
    return redirect('dashboard')

# --- Compare ---
def compare_view(request):
    compare_list = request.session.get('compare_list', [])
    products = Product.objects.filter(id__in=compare_list)
    return render(request, 'compare.html', {'products': products})

def add_to_compare(request, product_id):
    compare_list = request.session.get('compare_list', [])
    if product_id not in compare_list:
        if len(compare_list) >= 4:
            messages.warning(request, "You can compare up to 4 products only.")
        else:
            compare_list.append(product_id)
            request.session['compare_list'] = compare_list
            messages.success(request, "Product added to comparison list.")
    else:
        messages.info(request, "Product already in comparison list.")
    return redirect('compare_view')

def remove_from_compare(request, product_id):
    compare_list = request.session.get('compare_list', [])
    if product_id in compare_list:
        compare_list.remove(product_id)
        request.session['compare_list'] = compare_list
        messages.success(request, "Product removed from comparison list.")
    return redirect('compare_view')

def clear_compare(request):
    if 'compare_list' in request.session:
        del request.session['compare_list']
    return redirect('compare_view')

@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'invoice.html', {'order': order})

@login_required
def supervisor_dashboard(request):
    if not request.user.is_staff and not request.user.groups.filter(name='Supervisor').exists():
        messages.error(request, "Access Denied: You are not authorized to view this page.")
        return redirect('home')
        
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_users = User.objects.count()
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    context = {
        'total_orders': total_orders,
        'total_products': total_products,
        'total_users': total_users,
        'recent_orders': recent_orders,
    }
    return render(request, 'supervisor_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Superuser privileges required.")
        return redirect('home')
        
    # High-level stats
    total_sales = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    total_products = Product.objects.count()
    active_supervisors = User.objects.filter(groups__name='Supervisor').count()
    
    # Recent activity
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    new_users = User.objects.order_by('-date_joined')[:5]
    
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_products': total_products,
        'active_supervisors': active_supervisors,
        'recent_orders': recent_orders,
        'new_users': new_users,
    }
    return render(request, 'admin_dashboard.html', context)
