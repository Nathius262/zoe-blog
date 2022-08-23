from django.shortcuts import render
from profileAccount.models import Account
from blogPost.views import get_blog_queryset
from operator import attrgetter
from blogPost.models import BlogPost, Category


def home_screen_view(request):
    context = {}

    query = ""
    if request.GET:
        query = request.GET.get('q', '')
        context['query'] = str(query)

    posts = sorted(get_blog_queryset(query), key=attrgetter('date_updated'), reverse=True)

    accounts = Account.objects.all()

    category = Category.objects.all()

    context = {
        'popular_posts': BlogPost.objects.order_by('-hit_count_generic__hits')[:4],
        'latest_posts': BlogPost.objects.order_by('-date_published')[:4],
        'posts': posts,
        'accounts': accounts,
        'category': category,
        'query': query,
    }
    return render(request, "home/home.html", context)
