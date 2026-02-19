from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from .models import (
    HomeSettings, NavbarSettings, HeroMainSettings, HeroSocialSettings, 
    AboutSectionSettings, ContactSectionSettings, FooterSettings,
    BlogSectionSettings, ExpertiseSectionSettings,
    Project, Service, ServiceBooking, ContactMessage,
    AcademicBackground, SkillCategory, SkillItem, Experience, 
    ProfessionalTraining, GlobalCertificationModel, ProfessionalTrainingModel, BlogPost, ProjectImage
)

# Base Admin for settings (Singleton behavior)
class BaseSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if self.model.objects.exists():
            obj = self.model.objects.first()
            return HttpResponseRedirect(reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change', args=[obj.pk]))
        return super().changelist_view(request, extra_context=extra_context)

# 1. Navbar Content
@admin.register(NavbarSettings)
class NavbarSettingsAdmin(BaseSettingsAdmin):
    fields = ['site_title', 'logo', 'favicon']

# 2. Hero Section Content
@admin.register(HeroMainSettings)
class HeroMainSettingsAdmin(BaseSettingsAdmin):
    fields = ['hero_greeting', 'hero_name', 'hero_subtitle', 'hero_description', 'hero_profile_image', 'resume_file']

@admin.register(HeroSocialSettings)
class HeroSocialSettingsAdmin(BaseSettingsAdmin):
    fields = [
        'linkedin_url', 'linkedin_logo',
        'facebook_url', 'facebook_logo',
        'github_url', 'github_logo',
        'instagram_url', 'instagram_logo',
        'x_url', 'x_logo'
    ]

# 3. About Me Content
@admin.register(AboutSectionSettings)
class AboutSectionSettingsAdmin(BaseSettingsAdmin):
    fields = ['about_description', 'about_who_am_i']

@admin.register(AcademicBackground)
class AcademicBackgroundAdmin(admin.ModelAdmin):
    list_display = ['institution_name', 'degree_name', 'order']
    list_editable = ['order']
    exclude = ['settings']

class SkillItemInline(admin.TabularInline):
    model = SkillItem
    extra = 1

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']
    inlines = [SkillItemInline]
    exclude = ['settings']

# 4. My Experience Content
@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'designation', 'start_date', 'end_description')
    list_filter = ('is_current', 'start_date')
    search_fields = ('company_name', 'designation')

    def end_description(self, obj):
        return "Present" if obj.is_current or not obj.end_date else obj.end_date
    end_description.short_description = "End Date"

# 5. My Expertise Content
@admin.register(ProfessionalTrainingModel)
class ProfessionalTrainingAdmin(admin.ModelAdmin):
    list_display = ['course_name', 'organization_name', 'mode', 'order']
    list_editable = ['order']
    list_filter = ['mode']
    exclude = ['category', 'settings']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(category='TRAINING')

    def save_model(self, request, obj, form, change):
        obj.category = 'TRAINING'
        super().save_model(request, obj, form, change)

@admin.register(GlobalCertificationModel)
class GlobalCertificationAdmin(admin.ModelAdmin):
    list_display = ['course_name', 'organization_name', 'mode', 'order']
    list_editable = ['order']
    list_filter = ['mode']
    exclude = ['category', 'settings']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(category='CERTIFICATION')

    def save_model(self, request, obj, form, change):
        obj.category = 'CERTIFICATION'
        super().save_model(request, obj, form, change)

# 6. Featured Projects Content
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'tech_stack', 'created_at')
    search_fields = ('title', 'tech_stack')
    inlines = [ProjectImageInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'image')
        }),
        ('Technologies & Links', {
            'fields': ('tech_stack', 'live_link', 'repo_link'),
            'description': "Enter technologies separated by commas."
        }),
    )

# 7. My Services Content
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']
    fields = ['title', 'icon_class', 'features', 'order']

# 8. My Blog Content
@admin.register(BlogSectionSettings)
class BlogSectionSettingsAdmin(BaseSettingsAdmin):
    fields = ['blog_section_description']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'views', 'created_at')
    search_fields = ('title', 'content', 'category')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('category', 'created_at')
    exclude = ['settings']

# 9. Contact
@admin.register(ContactSectionSettings)
class ContactSectionSettingsAdmin(BaseSettingsAdmin):
    fields = ['email', 'phone', 'address'] 

# 10. Footer Content
@admin.register(FooterSettings)
class FooterSettingsAdmin(BaseSettingsAdmin):
    fields = ['footer_copyright']

# User Submissions
@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'email', 'preferred_date', 'created_at']
    list_filter = ['service', 'preferred_date']
    readonly_fields = ['created_at']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'created_at']
    readonly_fields = ['created_at']

# Unregister unused/helper
# SkillCategory is registered above for 'Expertise' section. I will check.
# Yes, it is.

# Cleanup
try:
    from django.contrib.auth.models import Group
    admin.site.unregister(Group)
    from allauth.account.models import EmailAddress
    admin.site.unregister(EmailAddress)
    from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
    admin.site.unregister(SocialApp)
    admin.site.unregister(SocialAccount)
    admin.site.unregister(SocialToken)
except:
    pass

