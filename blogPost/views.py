from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from hitcount.views import HitCountDetailView

from blogPost.models import BlogPost, Category, Like
from blogPost.forms import CreateBlogPostForm, EditBlogPostForm, CreateCategoryForm, NewCommentForm, CommentForm
from profileAccount.models import Account
from django.views.generic import ListView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from operator import attrgetter


# SEARCH FUNCTION
def get_blog_queryset(query=None):
    queryset = []
    queries = query.split(" ")
    for q in queries:
        posts = BlogPost.objects.all().filter(
            Q(title__icontains=q) |
            Q(body__icontains=q)
        ).distinct()
        for post in posts:
            queryset.append(post)
    return list(set(queryset))


# Create your views here.
def category_list(request):
    category = Category.objects.all()
    context = {'category_list': category}

    return context


# create blog
def create_blog_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('must_authenticate')

    form = CreateBlogPostForm(request.POST, request.FILES)
    item = request.POST.getlist('obj')

    if form.is_valid():
        obj = form.save(commit=False)
        author = Account.objects.filter(email=user.email).first()
        obj.author = author
        obj.save()

        for cat in item:
            cat_list = Category.objects.all().filter(category_name=cat).first()
            p = obj.category.add(cat_list.id)
            print(p)

        form = CreateBlogPostForm()

    author = Account.objects.filter(email=user.email).first()
    context = {
        'form': form,
        'author': author,
    }

    return render(request, "blogPost/create_blog.html", context)


# edit blog post
def edit_blog_view(request, slug):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must_authenticate')

    blog_post = get_object_or_404(BlogPost, slug=slug)
    cat = blog_post.category.all()

    if request.POST:
        form = EditBlogPostForm(request.POST, request.FILES, instance=blog_post)

        for item in blog_post.category.all():
            blog_post.category.remove(item.id)

        # print(blog_post.category.all())

        cat_obj = request.POST.getlist('obj')

        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()

            for cat_item in cat_obj:
                cat_list = Category.objects.all().filter(category_name=cat_item).first()
                obj.category.add(cat_list.id)

            # print(blog_post.category.all())

            messages.success(request, "Updated Successfully!")

    form = EditBlogPostForm(
        initial={
            "title": blog_post.title,
            "category": cat,
            "body": blog_post.body,
            "image": blog_post.image,
        }
    )

    context['form'] = form
    return render(request, 'blogPost/edit_blog.html', context)


POSTS_PER_PAGE = 9


# blog pages
def blog_view(request):
    context = {}

    query = ""
    if request.GET:
        query = request.GET.get('q', '')
        context['query'] = str(query)

    all_post = sorted(get_blog_queryset(query), key=attrgetter('date_updated'), reverse=True)
    context['all_post'] = all_post

    # Pagination
    page = request.GET.get('page', 1)
    all_post_paginator = Paginator(all_post, POSTS_PER_PAGE)

    try:
        all_post = all_post_paginator.page(page)
    except PageNotAnInteger:
        all_post = all_post_paginator.page(POSTS_PER_PAGE)
    except EmptyPage:
        all_post = all_post_paginator.page(all_post_paginator.num_pages)
    context['all_post'] = all_post

    return render(request, 'blogPost/blog.html', context)


# single blog page
def single_post_view(request, post):
    post = get_object_or_404(BlogPost, slug=post)

    likes = Like.objects.all().filter(postLike=post, value='Like').count()
    dislikes = Like.objects.all().filter(postLike=post, value='Unlike').count()

    comments = post.comments.all()
    if not request.user.is_authenticated:
        messages.info(request, "You must sign up to like this page")

    context = {'post': post,
               'comments': comments,
               'guess_comment_form': NewCommentForm(),
               'user_comment_form': CommentForm(),
               'user': request.user,
               'author_pix': post.author.image_profile,
               'likes': likes,
               'dislikes': dislikes,
               }
    return render(request, 'blogPost/single_post.html', context)


class SinglePostView(HitCountDetailView):
    model = BlogPost
    template_name = 'blogPost/detail_blog.html'
    context_object_name = 'post'
    slug_field = 'slug'
    count_hit = True

    def get_queryset(self):
        posts = BlogPost.objects.all().filter(slug=self.kwargs['slug'])
        return posts

    def get_context_data(self, **kwargs):
        context = super(SinglePostView, self).get_context_data(**kwargs)
        user = self.request.user
        post = self.get_queryset()
        post = post.first()

        likes = Like.objects.all().filter(postLike=post, value='Like').count()
        dislikes = Like.objects.all().filter(postLike=post, value='Unlike').count()

        cat = post.category.all()

        comments = post.comments.all()
        if not user.is_authenticated:
            messages.info(self.request, "You must sign up to like this page")

        context.update({
            'popular_posts': BlogPost.objects.order_by('-hit_count_generic__hits')[:3],
            'comments': comments,
            'guess_comment_form': NewCommentForm(),
            'user_comment_form': CommentForm(),
            'user': user,
            'author_pix': post.author.image_profile,
            'cat': cat,
            'likes': likes,
            'dislikes': dislikes,
        })
        return context


def like_view(request, post):
    post = get_object_or_404(BlogPost, slug=post)
    test = post.get_absolute_url()
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_value = request.POST.get('post_value')

        if Like.objects.all().filter(user=user, postLike_id=post_id):
            like_value = Like.objects.filter(user=user, postLike_id=post_id).first()
            if (like_value.value == "Like") and (post_value == "Like"):
                Like.objects.all().filter(user=user, postLike_id=post_id).delete()
            elif (like_value.value == "Like") and (post_value == "Unlike"):
                like_value.value = "Unlike"
                like_value.save()
            elif (like_value.value == "Unlike") and (post_value == "Like"):
                like_value.value = "Like"
                like_value.save()
            else:
                Like.objects.all().filter(user=user, postLike_id=post_id).delete()
        else:
            Like.objects.create(user=user, postLike_id=post_id, value=post_value)
    return redirect(test)


def comment_view(request, post):
    post = get_object_or_404(BlogPost, slug=post)
    test = post.get_absolute_url()
    user = request.user
    if not request.user.is_authenticated:
        if request.method == 'POST':
            comment_form = NewCommentForm(request.POST)
            if comment_form.is_valid():
                user_comment = comment_form.save(commit=False)
                user_comment.post = post
                user_comment.save()
    else:
        if request.method == 'POST':
            acct = Account.objects.filter(email=user.email).first()
            name_comment = acct.name
            email_comment = acct.email
            username_comment = acct.username

            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                user_comment = comment_form.save(commit=False)
                # get the user profile details if authenticated

                user_comment.name_comment = name_comment
                user_comment.email_comment = email_comment
                user_comment.username_comment = username_comment
                user_comment.post = post
                user_comment.save()

    return redirect(test)


def delete_post(request, post):
    posts = BlogPost.objects.all().filter(slug=post)
    post = get_object_or_404(BlogPost, slug=post)
    test = post.get_absolute_url()
    comments = post.comments.all()

    if request.POST:
        get_post = request.POST.get('get_post')

        if "ok" in get_post:
            posts.delete()
            return redirect("home")
        else:
            return redirect(test)

    context = {
        'post': post,
        'test': test,
        'comments': comments,
        'user': request.user,
    }

    return render(request, 'blogPost/snippets/delete_post.html', context)


# category view
class CatListView(ListView):
    template_name = 'blogPost/category.html'
    context_object_name = 'catlist'

    # SEARCH FUNCTION CATEGORY
    def get_category_queryset(self, query=None):
        queryset = []
        queries = query.split(" ")
        for q in queries:
            posts = BlogPost.objects.order_by('-date_published').filter(
                category__category_name=self.kwargs['category']).filter(
                Q(title__icontains=q) |
                Q(body__icontains=q)
            ).distinct()
            for post in posts:
                queryset.append(post)
        return list(set(queryset))

    def get_queryset(self):
        content = {}

        query = ""
        if self.request.GET:
            query = self.request.GET.get('q', '')
            content['query'] = str(query)

        post = sorted(self.get_category_queryset(query), key=attrgetter('date_updated'), reverse=True)

        content = {
            'cat': self.kwargs['category'],
            'posts': post,
            'query': query,

        }

        return content


# create category view
def create_category_view(request):
    form = CreateCategoryForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Successfully added new category")
    content = {'forms': form}

    return content
