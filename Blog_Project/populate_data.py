import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings")
django.setup()

from blog.models import Category, Post, HomeContent, User

# Create Categories
cats = ['Technology', 'Lifestyle', 'Programming', 'Business']
for c in cats:
    Category.objects.get_or_create(name=c)
    print(f"Category '{c}' ensured.")

# Create HomeContent
if not HomeContent.objects.exists():
    HomeContent.objects.create(
        marquee_text="Welcome to the new BlogPro! Check out our latest articles.",
        short_description="Welcome to BlogPro",
        motto="Insightful articles for professionals."
    )
    print("HomeContent created.")

# Create Welcome Post
try:
    admin_user = User.objects.get(username='admin')
    tech_cat = Category.objects.get(name='Technology')
    if not Post.objects.filter(title="Welcome to BlogPro").exists():
        Post.objects.create(
            title="Welcome to BlogPro",
            content="This is the first post on your new blog. You can edit or delete it from the admin panel.",
            category=tech_cat,
            author=admin_user,
            status='published'
        )
        print("Default post created.")
except Exception as e:
    print(f"Error creating default post: {e}")
