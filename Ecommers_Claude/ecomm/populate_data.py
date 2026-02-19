import os
import django
import random
from decimal import Decimal
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
django.setup()

from myecom.models import User, Category, Brand, Product, ProductImage

def populate():
    print("Creating superuser...")
    if not User.objects.filter(email='admin@example.com').exists():
        User.objects.create_superuser('admin@example.com', 'admin123', first_name='Admin', last_name='User')
        print("Superuser created: admin@example.com / admin123")
    else:
        print("Superuser already exists.")

    print("Creating categories...")
    categories = ['Electronics', 'Fashion', 'Home & Living', 'Beauty', 'Sports']
    cat_objs = []
    for cat in categories:
        c, created = Category.objects.get_or_create(name=cat)
        cat_objs.append(c)

    print("Creating brands...")
    brands = ['Nike', 'Samsung', 'Apple', 'Sony', 'Zara']
    brand_objs = []
    for brand in brands:
        b, created = Brand.objects.get_or_create(name=brand)
        brand_objs.append(b)

    print("Creating products...")
    for i in range(20):
        name = f"Sample Product {i+1}"
        cat = random.choice(cat_objs)
        brand = random.choice(brand_objs)
        price = Decimal(random.uniform(10.0, 1000.0)).quantize(Decimal('0.01'))
        
        product, created = Product.objects.get_or_create(
            name=name,
            defaults={
                'category': cat,
                'brand': brand,
                'base_price': price,
                'sku': f"SKU-{i+1000}",
                'description': "This is a great product with amazing features. Buy it now!",
                'stock_status': 'in_stock',
                'stock_quantity': 100,
                'is_featured': random.choice([True, False]),
                'is_trending': random.choice([True, False]),
                'is_new': random.choice([True, False]),
            }
        )
        
        if created:
            # Add images
            ProductImage.objects.create(
                product=product,
                image_url=f"https://picsum.photos/seed/{product.id}/800/800",
                is_primary=True
            )
            ProductImage.objects.create(
                product=product,
                image_url=f"https://picsum.photos/seed/{product.id}-2/800/800",
                display_order=1
            )

    print("Population complete.")

if __name__ == '__main__':
    populate()
