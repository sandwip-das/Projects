from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from .models import Post, Category, Tag, Profile, Comment, PostInteraction, HomeContent, ImportantLink
from .forms import ProfileForm, CommentForm, ContactForm, UserUpdateForm, PostForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

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
        from django.http import Http404
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

from django.http import JsonResponse
from django.template.loader import render_to_string

# ... (Previous imports kept implicitly by context matching, but adding JsonResponse)

# Note: Ideally we should add JsonResponse to the imports at top, but for this editing tool, 
# I will rewrite the relevant views and assume top-level imports are handled or I will add them if I can.
# Actually, I'll just rewrite the views down here and risk the import error? 
# No, I must ensure valid python. I'll simply add the import line at the top if I could, but I can't jump around.
# I will use 'from django.http import JsonResponse' inside the function if needed, or hope it's there? 
# It's not there. I will modify the top of the file separately? 
# No, I will modify the Functions to import inside them or use the replace tool to swap the top imports first.
# Wait, I can just replace the functions. I'll add the import inside the functions for safety 
# or Replace the whole file content for imports? No, too large.
# use 'from django.http import JsonResponse' inside the view functions.

@login_required
def post_interaction(request, slug):
    from django.http import JsonResponse
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json')
    
    post = get_object_or_404(Post, slug=slug)
    # Handle AJAX for cleaner UI
    if is_ajax and request.method == 'POST':
        import json
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
    from django.http import JsonResponse
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
                # Return the rendered HTML for the new comment to append via JS
                # Constructing a simple dictionary of data is easier, or rendering a partial.
                # Since we are inline, let's just return data and let JS build it, OR render a small template.
                # simpler: Just return data.
                from django.utils.timesince import timesince
                return JsonResponse({
                    'message': 'Comment added!',
                    'count': post.comments.filter(active=True, parent__isnull=True).count(),
                    'comment': {
                        'id': comment.pk,
                        'user': comment.user.username,
                        'profile_picture_url': comment.user.profile.profile_picture.url if comment.user.profile.profile_picture else None,
                        'initial': comment.user.username[0].upper(),
                        'created_at': timesince(comment.created_at) + " ago",
                        'content': comment.content
                    }
                })
                
            messages.success(request, 'Comment added!')
            
    return redirect('post_detail', slug=slug)

@login_required
def dashboard(request):
    if not request.user.is_staff:
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

    # Counts
    draft_count = my_drafts.count()
    admin_draft_count = admin_drafts.count() if admin_drafts else 0
    
    context = {
        'total_posts': total_posts,
        'total_views': total_views,
        'total_likes': total_likes,
        'my_drafts': my_drafts,
        'my_published': my_published,
        'admin_drafts': admin_drafts,
        'draft_count': draft_count,
        'admin_draft_count': admin_draft_count,
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
        return self.request.user.is_staff

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user.is_superuser:
            return True
        if self.request.user == post.author and self.request.user.is_staff:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.html'
    
    def test_func(self):
        post = self.get_object()
        if self.request.user.is_superuser:
            return True
        if self.request.user == post.author and self.request.user.is_staff:
            return True
        return False

@login_required
def comment_edit(request, pk):
    from django.http import JsonResponse
    import json
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
    from django.http import JsonResponse
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
