from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings as django_settings
from .models import HomeSettings, Skill, Project, SocialLink, SkillCategory, Experience, Service, ServiceBooking, ContactMessage, AcademicBackground, ProfessionalTraining, AboutMeItem, BlogPost
from .forms import ServiceBookingForm, ContactForm

from django.contrib.auth.models import User

def home(request):
    # Get the single instance of HomeSettings
    site_settings = HomeSettings.objects.first()
    if not site_settings:
        site_settings = HomeSettings.objects.create()

    if request.method == 'POST':
        # Default fallback
        admin_email = getattr(django_settings, 'DEFAULT_FROM_EMAIL', 'admin@example.com')
        
        # Try to find a superuser's email to start sending emails to
        superuser = User.objects.filter(is_superuser=True).order_by('id').first()
        if superuser and superuser.email:
            admin_email = superuser.email
        
        if 'service_id' in request.POST:
            form = ServiceBookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                try:
                    service = Service.objects.get(id=request.POST.get('service_id'))
                    booking.service = service
                    booking.save()
                    
                    # Improved Email Logic
                    subject = f"New Service Booking: {service.title} from {booking.name}"
                    body = f"New booking request received:\n\nService: {service.title}\nName: {booking.name}\nPhone: {booking.phone}\nEmail: {booking.email}\nDate: {booking.preferred_date}\nTime: {booking.preferred_time}\nMessage: {booking.additional_message}"
                    
                    email_msg = EmailMessage(
                        subject=subject,
                        body=body,
                        from_email=getattr(django_settings, 'DEFAULT_FROM_EMAIL', 'noreply@portfolio.com'),
                        to=[admin_email],
                        reply_to=[booking.email]
                    )
                    email_msg.send(fail_silently=False)
                    
                    messages.success(request, "Your booking request has been submitted successfully!")
                    return redirect('home')
                except Service.DoesNotExist:
                    messages.error(request, "Selected service does not exist.")
        
        elif 'contact_form' in request.POST:
            form = ContactForm(request.POST)
            if form.is_valid():
                contact = form.save()
                
                # Beautifully Formatted Email Logic
                subject = f"Portfolio Contact: {contact.subject} - from {contact.name}"
                
                body = f"""
You have received a new message from your portfolio website contact form.

--------------------------------------------------
SENDER DETAILS:
Name:    {contact.name}
Email:   {contact.email}
Phone:   {contact.phone if contact.phone else 'Not provided'}
Subject: {contact.subject}

--------------------------------------------------
MESSAGE:
{contact.message}

--------------------------------------------------
This email was sent automatically from your portfolio website.
"""
                
                email_msg = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=getattr(django_settings, 'DEFAULT_FROM_EMAIL', 'noreply@portfolio.com'),
                    to=[admin_email],
                    reply_to=[contact.email]
                )
                email_msg.send(fail_silently=False)
                
                messages.success(request, "Your message has been sent successfully!")
                return redirect('home')
            else:
                messages.error(request, "Please fix the errors in the contact form.")

    skills = Skill.objects.all()
    skill_categories = SkillCategory.objects.all().prefetch_related('items')
    # Use generic AboutMeItem querysets
    focus_items = AboutMeItem.objects.filter(category='FOCUS')
    key_skill_items = AboutMeItem.objects.filter(category='SKILL')
    role_items = AboutMeItem.objects.filter(category='ROLE')
    
    projects = Project.objects.all().order_by('-created_at')
    social_links = SocialLink.objects.all()
    experiences = Experience.objects.all()
    services = Service.objects.all()
    academic_background = AcademicBackground.objects.all()
    professional_trainings = ProfessionalTraining.objects.filter(category='TRAINING')
    global_certifications = ProfessionalTraining.objects.filter(category='CERTIFICATION')
    blog_posts = BlogPost.objects.all().order_by('-created_at')
    
    booking_form = ServiceBookingForm()
    contact_form = ContactForm()

    context = {
        'settings': site_settings,
        'skills': skills,
        'skill_categories': skill_categories,
        'focus_items': focus_items,
        'key_skill_items': key_skill_items,
        'role_items': role_items,
        'projects': projects,
        'social_links': social_links,
        'experiences': experiences,
        'services': services,
        'academic_background': academic_background,
        'professional_trainings': professional_trainings,
        'global_certifications': global_certifications,
        'blog_posts': blog_posts,

        'booking_form': booking_form,
        'contact_form': contact_form
    }
    return render(request, 'home.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    post.views += 1
    post.save()
    return render(request, 'blog_detail.html', {'post': post})
