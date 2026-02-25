from django.contrib import admin
from django import forms
from django.db import models
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline
from .models import (
    HomeSettings, NavbarSettings, HeroMainSettings, HeroSocialSettings, 
    AboutSectionSettings, ContactSectionSettings, FooterSettings,
    TechnicalSkillsSection,
    Project, Service, ServiceBooking, ContactMessage,
    AcademicBackground, SkillCategory, Experience, 
    ProfessionalTraining, GlobalCertificationModel, ProfessionalTrainingModel, 
    BlogPost, ProjectImage, Skill, SkillItem, Review, NavbarMenu,
    BlogPostImage, BlogComment, BlogReaction, BlogViewTrack,
    UserProfile, UserManagement
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

# 0. Navbar Menus Inline
class NavbarMenuInline(admin.TabularInline):
    model = NavbarMenu
    extra = 1
    fields = ['name', 'section_id', 'order']

# 1. Navbar Content
@admin.register(NavbarSettings)
class NavbarSettingsAdmin(BaseSettingsAdmin):
    fields = ['site_title', 'logo', 'favicon']
    inlines = [NavbarMenuInline]

# 2. Hero Section Content
@admin.register(HeroMainSettings)
class HeroMainSettingsAdmin(BaseSettingsAdmin):
    fields = ['hero_greeting', 'hero_name', 'hero_description', 'hero_profile_image', 'resume_file']

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
    fields = ['about_title', 'about_description', 'about_who_am_i']

@admin.register(AcademicBackground)
class AcademicBackgroundAdmin(admin.ModelAdmin):
    list_display = ['institution_name', 'degree_name', 'order']
    list_editable = ['order']
    exclude = ['settings']

# 5. Technical Skills (Unified Nested Interface)
class SkillItemInline(NestedTabularInline):
    model = SkillItem
    extra = 1
    fields = ('name', 'order')
    sortable_field_name = "order"

class SkillCategoryInline(NestedStackedInline):
    model = SkillCategory
    extra = 0
    fields = ('name', 'order')
    inlines = [SkillItemInline]
    exclude = ['skills_list']
    sortable_field_name = "order"

class SkillCardInline(NestedTabularInline):
    model = Skill
    extra = 1
    fields = ('image', 'name', 'order')
    sortable_field_name = "order"

@admin.register(TechnicalSkillsSection)
class TechnicalSkillsSectionAdmin(NestedModelAdmin):
    # Singleton Logic
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

    # UI Configuration
    fieldsets = (
        (None, {
            'fields': ('technical_skills_description',),
            'description': "Manage the Technical Skills section. Add Categories, and within each Category, add Skill Items."
        }),
    )
    inlines = [SkillCategoryInline, SkillCardInline]

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

class BlogPostImageInline(admin.TabularInline):
    model = BlogPostImage
    extra = 1
    fields = ['image', 'caption', 'order']
    sortable_field_name = "order"

# Blog Analytics Inlines (Dashboard & Metrics)
class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    readonly_fields = ['user', 'content', 'created_at']
    fields = ['user', 'content', 'created_at']
    can_delete = False
    verbose_name = "Comment"
    verbose_name_plural = "Comments"

class BlogReactionInline(admin.TabularInline):
    model = BlogReaction
    extra = 0
    readonly_fields = ['user', 'reaction', 'created_at']
    fields = ['user', 'reaction', 'created_at']
    can_delete = False
    verbose_name = "Reaction"
    verbose_name_plural = "Reactions"

class BlogViewTrackInline(admin.TabularInline):
    model = BlogViewTrack
    extra = 0
    readonly_fields = ['display_user_info', 'contact_number', 'ip_address', 'browsing_source', 'created_at']
    fields = ['display_user_info', 'contact_number', 'ip_address', 'browsing_source', 'created_at']
    can_delete = False
    verbose_name = "View Track"
    verbose_name_plural = "View Tracks"

    def display_user_info(self, obj):
        if obj.user:
            name = obj.user.get_full_name() or obj.user.username
            return f"{name}, {obj.user.email}"
        return "Anonymous Visitor"
    display_user_info.short_description = "Visitor Details (Name, Email)"

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    change_list_template = "admin/core/blogpost/change_list.html"
    list_display = (
        'title', 'category', 'total_views', 'total_likes', 
        'total_dislikes', 'total_comments', 'created_at'
    )
    search_fields = ('title', 'content', 'category')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('category', 'created_at')
    
    # Combined Inlines: Post Editing + Analytics
    inlines = [
        BlogPostImageInline,
        BlogViewTrackInline,
        BlogReactionInline,
        BlogCommentInline
    ]
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'category', 'content')
        }),
        ('Statistics', {
            'fields': ('views',),
            'classes': ('collapse',),
            'description': "Quick stats counter. See detailed View Tracks below."
        }),
    )
    exclude = ['settings']

    class Media:
        js = ('js/blog_admin.js',)
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',)
        }

    def get_queryset(self, request):
        from django.db.models import Count, Q
        qs = super().get_queryset(request)
        return qs.annotate(
            total_likes=Count('reactions', filter=Q(reactions__reaction='like'), distinct=True),
            total_dislikes=Count('reactions', filter=Q(reactions__reaction='dislike'), distinct=True),
            total_comments=Count('comments', distinct=True),
            total_view_tracks=Count('view_tracks', distinct=True)
        )

    def changelist_view(self, request, extra_context=None):
        if request.method == 'POST' and 'update_blog_description' in request.POST:
            description = request.POST.get('blog_section_description')
            settings = HomeSettings.load()
            settings.blog_section_description = description
            settings.save()
            from django.contrib import messages
            messages.success(request, "Blog section description updated successfully.")
            return HttpResponseRedirect(request.get_full_path())

        extra_context = extra_context or {}
        settings = HomeSettings.load()
        extra_context['blog_section_description'] = settings.blog_section_description
        extra_context['total_website_views'] = BlogViewTrack.objects.count()
        extra_context['total_likes'] = BlogReaction.objects.filter(reaction='like').count()
        extra_context['total_dislikes'] = BlogReaction.objects.filter(reaction='dislike').count()
        extra_context['total_comments'] = BlogComment.objects.count()
        return super().changelist_view(request, extra_context=extra_context)

    # Metric Columns for List View
    def total_views(self, obj):
        return obj.total_view_tracks
    total_views.short_description = "Views"
    total_views.admin_order_field = "total_view_tracks"

    def total_likes(self, obj):
        return obj.total_likes
    total_likes.short_description = "Likes"
    total_likes.admin_order_field = "total_likes"

    def total_dislikes(self, obj):
        return obj.total_dislikes
    total_dislikes.short_description = "Dislikes"
    total_dislikes.admin_order_field = "total_dislikes"

    def total_comments(self, obj):
        return obj.total_comments
    total_comments.short_description = "Comments"
    total_comments.admin_order_field = "total_comments"

# 9. Contact
@admin.register(ContactSectionSettings)
class ContactSectionSettingsAdmin(BaseSettingsAdmin):
    fields = ['contact_heading', 'contact_sub_heading', 'contact_text'] 

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

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'profession', 'location', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    search_fields = ['name', 'comment']
    list_editable = ['is_approved']
    
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"

# 12. User Management
from django.contrib.auth.admin import UserAdmin

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Info'
    fk_name = 'user'
    
class UserBlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    readonly_fields = ['post', 'content', 'created_at']
    fields = ['post', 'content', 'created_at']
    can_delete = True
    verbose_name = "User's Comment"
    verbose_name_plural = "User's Comments"

class UserBlogReactionInline(admin.TabularInline):
    model = BlogReaction
    extra = 0
    readonly_fields = ['post', 'reaction', 'created_at']
    fields = ['post', 'reaction', 'created_at']
    can_delete = True
    verbose_name = "User's Reaction"
    verbose_name_plural = "User's Reactions"

class UserBlogViewTrackInline(admin.TabularInline):
    model = BlogViewTrack
    extra = 0
    readonly_fields = ['post', 'ip_address', 'user_agent', 'browsing_source', 'created_at']
    fields = ['post', 'ip_address', 'user_agent', 'browsing_source', 'created_at']
    can_delete = False
    verbose_name = "User's View Track"
    verbose_name_plural = "User's View Tracks"

@admin.register(UserManagement)
class UserManagementAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    inlines = [UserProfileInline, UserBlogCommentInline, UserBlogReactionInline, UserBlogViewTrackInline]

    def has_add_permission(self, request):
        return False
        
    def get_fieldsets(self, request, obj=None):
        return (
            (None, {'fields': ('username', 'password')}),
            ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
            ('Account Status', {'fields': ('is_active',)}),
            ('Important dates', {'fields': ('last_login', 'date_joined')}),
        )

# Unregister unused/helper
# SkillCategory is registered above for 'Expertise' section. I will check.
# Yes, it is.

# Cleanup - Unregister Group and User (not needed for single-user portfolio)
try:
    from django.contrib.auth.models import Group, User
    admin.site.unregister(Group)
    admin.site.unregister(User)
except:
    pass
