import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.timesince import timesince
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Sum
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string

from .models import Post, Category, Tag, Profile, Comment, PostInteraction, HomeContent, ImportantLink, PostEditHistory
from .forms import ProfileForm, CommentForm, ContactForm, UserUpdateForm, PostForm

# Helper for Role-Based Permissions
def is_editor(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Editor').exists())

def home(request):
    try:
        home_content = HomeContent.objects.latest('id')
    except HomeContent.DoesNotExist:
        home_content = None 
        
    most_read = Post.objects.filter(status='published').order_by('-views_count')[:5]
    latest_posts = Post.objects.filter(status='published').order_by('-created_at')
    
    featured_latest = None
    recent_list = []
    
    if latest_posts.exists():
        featured_latest = latest_posts[0]
        recent_list = latest_posts[1:] 
        
    links = ImportantLink.objects.all()
    
    context = {
        'home_content': home_content,
        'most_read': most_read,
        'featured_latest': featured_latest,
        'recent_list': recent_list,
        'links': links,
    }
    return render(request, 'blog/home.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Restrict Drafts
    if post.status == 'draft' and request.user != post.author and not request.user.is_superuser:
        raise Http404("Post not found")
    
    post.views_count += 1
    post.save()
    
    comments = post.comments.filter(active=True, parent__isnull=True).order_by('-created_at')
    comment_form = CommentForm()
    
    user_interaction = None
    if request.user.is_authenticated:
        try:
            interaction = PostInteraction.objects.get(user=request.user, post=post)
            user_interaction = interaction.interaction_type
        except PostInteraction.DoesNotExist:
            user_interaction = None
            
    likes_count = post.interactions.filter(interaction_type='like').count()
    dislikes_count = post.interactions.filter(interaction_type='dislike').count()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_interaction': user_interaction,
        'likes_count': likes_count,
        'dislikes_count': dislikes_count,
    }
    return render(request, 'blog/post_detail.html', context)

def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published').order_by('-created_at')
    return render(request, 'blog/category_posts.html', {'category': category, 'posts': posts})

def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    return render(request, 'blog/search_results.html', {'query': query, 'results': results})

@login_required
def profile(request):
    return render(request, 'blog/profile.html')

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=profile)
    return render(request, 'blog/edit_profile.html', {'u_form': u_form, 'p_form': p_form})

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Send email logic (mock)
            messages.success(request, 'Your message has been sent. We will contact you soon.')
            return redirect('home')
    return redirect('home')

@login_required
def post_interaction(request, slug):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json')
    post = get_object_or_404(Post, slug=slug)
    if is_ajax and request.method == 'POST':
        try:
            data = json.loads(request.body)
            interaction_type = data.get('interaction_type')
        except:
            interaction_type = request.POST.get('interaction_type')

        if interaction_type not in ['like', 'dislike']:
             return JsonResponse({'error': 'Invalid type'}, status=400)

        interaction, created = PostInteraction.objects.get_or_create(
            user=request.user, 
            post=post,
            defaults={'interaction_type': interaction_type}
        )
        
        if not created:
            if interaction.interaction_type == interaction_type:
                interaction.delete() # Toggle off
                user_interaction = None
            else:
                interaction.interaction_type = interaction_type
                interaction.save()
                user_interaction = interaction_type
        else:
            user_interaction = interaction_type
            
        likes_count = post.interactions.filter(interaction_type='like').count()
        dislikes_count = post.interactions.filter(interaction_type='dislike').count()
        
        return JsonResponse({
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
            'user_interaction': user_interaction
        })

    # Fallback for non-AJAX (Legacy support)
    interaction_type = request.POST.get('interaction_type')
    if interaction_type not in ['like', 'dislike']:
        return redirect('post_detail', slug=slug)
        
    interaction, created = PostInteraction.objects.get_or_create(
        user=request.user, 
        post=post,
        defaults={'interaction_type': interaction_type}
    )
    
    if not created:
        if interaction.interaction_type == interaction_type:
            interaction.delete()
        else:
            interaction.interaction_type = interaction_type
            interaction.save()
            
    return redirect('post_detail', slug=slug)

@login_required
def add_comment(request, slug):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent = Comment.objects.get(id=parent_id)
                    comment.parent = parent
                except Comment.DoesNotExist:
                    pass
            comment.save()
            
            if is_ajax:
                return JsonResponse({
                    'message': 'Comment added!',
                    'count': post.comments.filter(active=True, parent__isnull=True).count(),
                    'comment': {
                        'id': comment.pk,
                        'user': comment.user.username,
                        'profile_picture_url': comment.user.profile.profile_picture.url if hasattr(comment.user, 'profile') and comment.user.profile.profile_picture else None,
                        'initial': comment.user.username[0].upper(),
                        'created_at': timesince(comment.created_at) + " ago",
                        'content': comment.content
                    }
                })
                
            messages.success(request, 'Comment added!')
            
    return redirect('post_detail', slug=slug)

@login_required
def dashboard(request):
    if not is_editor(request.user):
        messages.error(request, "Access restricted to staff/editors.")
        return redirect('home')
        
    user_posts = Post.objects.filter(author=request.user)
    total_posts = user_posts.count()
    total_views = sum(p.views_count for p in user_posts)
    total_likes = PostInteraction.objects.filter(post__in=user_posts, interaction_type='like').count()
    
    # Drafts Logic
    my_drafts = user_posts.filter(status='draft').order_by('-created_at')
    my_published = user_posts.filter(status='published').order_by('-created_at')
    
    # Admin Global Drafts
    admin_drafts = None
    if request.user.is_superuser:
        admin_drafts = Post.objects.filter(status='draft').exclude(author=request.user).order_by('-created_at')

    # All Published Posts (For new tab)
    all_published_posts = Post.objects.filter(status='published').select_related('author').order_by('-created_at')

    # All Posts for Editor Tab (Superuser)
    # All Posts for Editor Tab (Superuser)
    all_posts = None
    admin_stats = []
    editor_stats = []
    
    if request.user.is_superuser:
        all_posts = Post.objects.filter(author__is_superuser=False).select_related('author').order_by('-created_at')
        
        # Calculate stats for all editors + superusers + staff
        # Added is_active=True to ensure we don't show deactivated users
        staff_users = User.objects.filter(Q(is_superuser=True) | Q(groups__name='Editor') | Q(is_staff=True), is_active=True).distinct().order_by('date_joined')
        for staff in staff_users:
            p_posts = Post.objects.filter(author=staff)
            p_count = p_posts.count()
            p_views = p_posts.aggregate(total=Sum('views_count'))['total'] or 0
            p_likes = PostInteraction.objects.filter(post__in=p_posts, interaction_type='like').count()
            p_comments = Comment.objects.filter(post__in=p_posts).count()
            
            stats_dict = {
                'user': staff,
                'total_posts': p_count,
                'total_views': p_views,
                'total_likes': p_likes,
                'total_comments': p_comments
            }
            
            if staff.is_superuser:
                admin_stats.append(stats_dict)
            else:
                editor_stats.append(stats_dict)

    # Calculate combined stats for the "All Staff" card
    combined_stats = {
        'total_posts': sum(d['total_posts'] for d in admin_stats + editor_stats),
        'total_views': sum(d['total_views'] for d in admin_stats + editor_stats),
        'total_likes': sum(d['total_likes'] for d in admin_stats + editor_stats),
        'total_comments': sum(d['total_comments'] for d in admin_stats + editor_stats),
    }

    # Counts
    draft_count = my_drafts.count()
    admin_draft_count = admin_drafts.count() if admin_drafts else 0

    context = {
        'total_posts': total_posts,
        'total_views': total_views,
        'total_likes': total_likes,
        'my_drafts': my_drafts,
        'my_published': my_published,
        'all_published_posts': all_published_posts,
        'admin_drafts': admin_drafts,
        'draft_count': draft_count,
        'admin_draft_count': admin_draft_count,
        'all_posts': all_posts,
        'combined_stats': combined_stats,
        'admin_stats': admin_stats,
        'editor_stats': editor_stats,
    }
    return render(request, 'blog/dashboard.html', context)

# CBVs for Post Management
class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
        
    def test_func(self):
        return is_editor(self.request.user)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        # Always update the last_edited fields to track the latest modification
        form.instance.last_edited_by = self.request.user
        form.instance.last_edited_at = timezone.now()
        response = super().form_valid(form)
        
        # Save to history log
        PostEditHistory.objects.create(
            post=self.object,
            editor=self.request.user
        )
        return response

    def test_func(self):
        # Editors can edit their own posts and strictly permissioned editors can edit others.
        # Since 'Editor' group has change_post, this covers both.
        return is_editor(self.request.user)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.html'
    
    def test_func(self):
        return is_editor(self.request.user)

@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Permissions
    if not (request.user.is_superuser or request.user == comment.post.author or request.user == comment.user):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        messages.error(request, "Permission denied.")
        return redirect('post_detail', slug=comment.post.slug)
    
    if request.method == 'POST':
        # AJAX Handling
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                content = data.get('content')
                if content:
                    comment.content = content
                    comment.save()
                    return JsonResponse({'message': 'Updated', 'content': comment.content})
                return JsonResponse({'error': 'Empty content'}, status=400)
            except:
                pass

        # Legacy Form Handling
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated!')
            return redirect('post_detail', slug=comment.post.slug)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment_form.html', {'form': form, 'comment': comment})

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Permissions
    if not (request.user.is_superuser or request.user == comment.post.author or request.user == comment.user):
         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Permission denied'}, status=403)
         messages.error(request, "Permission denied.")
         return redirect('post_detail', slug=comment.post.slug)
        
    if request.method == 'POST':
        post = comment.post
        comment.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
             return JsonResponse({
                 'message': 'Deleted',
                 'count': post.comments.filter(active=True, parent__isnull=True).count()
             })
        
        messages.success(request, 'Comment deleted!')
        return redirect('post_detail', slug=post.slug)
    
    return render(request, 'blog/comment_confirm_delete.html', {'comment': comment})

from django.contrib.auth.forms import PasswordResetForm
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.models import User

@require_POST
def ajax_password_reset(request):
    try:
        data = json.loads(request.body)
        action = data.get('action', 'verify')
        username = data.get('username')
        email = data.get('email')
        
        # Verify User Logic
        user = None
        if username and email:
            try:
                user_obj = User.objects.get(username=username)
                if user_obj.email.lower() == email.lower():
                    user = user_obj
            except User.DoesNotExist:
                pass
        
        if not user:
             return JsonResponse({'error': 'Email and User ID do not match.'}, status=400)

        if action == 'verify':
            return JsonResponse({'valid': True})
            
        if action == 'reset':
            new_password = data.get('new_password')
            if not new_password:
                return JsonResponse({'error': 'New password is required.'}, status=400)
                
            user.set_password(new_password)
            user.save()
            return JsonResponse({'message': 'Password has been reset successfully. Please login with your new password.'})
            
        return JsonResponse({'error': 'Invalid action.'}, status=400)
        
    except Exception as e:
         return JsonResponse({'error': str(e)}, status=500)
