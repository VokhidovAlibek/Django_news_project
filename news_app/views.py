from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin

from .models import News, Category
from .forms import ContactForm, CommentForm
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from news_app.custom_permissions import OnlyLoggedSuperUser
from django.contrib.auth.models import User


# Create your views here.

def news_list(request):
    news_list = News.published.all()
    context = {
        'news_list' : news_list
    }

    return render(request, 'news/news_list.html', context)

def news_detail(request, news):
    news = get_object_or_404(News, slug= news, status = News.Status.Published)
    context = {}

    #hitcount logic:
    hit_count = get_hitcount_model().objects.get_for_object(news)
    hits = hit_count.hits
    hitcontext = context['hitcount'] = {'pk':hit_count.pk}
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    if hit_count_response.hit_counted:
        hits = hits + 1
        hitcontext['hit_counted'] = hit_count_response.hit_counted
        hitcontext['hit_message'] = hit_count_response.hit_message
        hitcontext['total_hits'] = hits

                                                    # news.view_count = news.view_count + 1
                                                    # news.save()
    comments = news.comments.filter(active=True)
    comment_count = comments.count()
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.news = news
            new_comment.user = request.user
            new_comment.save()
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()


    context = {
        "news" : news,
        'comments' : comments,
        'new_comment' : news,
        'comment_form' : comment_form,
        'comment_count' : comment_count,
    }

    return render(request, 'news/news_detail.html', context)


# def homePageView(request):
#     categories = Category.objects.all()
#     news_list = News.published.all().order_by('-publish_time')[:4]
#     local_one = News.published.all().order_by('-publish_time').filter(category__name="Mahalliy")[:1]
#     local_news = News.published.all().order_by('-publish_time').filter(category__name="Mahalliy")[1:5]
#     context = {
#         'news_list' : news_list,
#         'categories' : categories,
#         'local_news' : local_news,
#         'local_one' : local_one,
#     }
#
#     return render(request, 'news/home.html', context)

class HomePageView(ListView):
    model = News
    template_name = 'news/home.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['news_list'] = News.published.all().order_by('-publish_time')[:5]
        context['mahalliy_news'] = News.published.all().filter(category__name='Mahalliy').order_by('-publish_time')[:5]
        context['horij_news'] = News.published.all().filter(category__name='Horij').order_by('-publish_time')[:5]
        context['sport_news'] = News.published.all().filter(category__name='Sport').order_by('-publish_time')[:5]
        context['texnoligiya_news'] = News.published.all().filter(category__name='Texnologiya').order_by('-publish_time')[:5]
        return context


# def contactPageView(request):
#     form = ContactForm(request.POST or None)
#     if  request.method == 'POST' and form.is_valid():
#         form.save()
#         return HttpResponse("<h2> Biz bilan bog'langaningiz uchun tashakkur!")
#     context = {
#         "form" : form
#     }
#     return render(request, 'news/contact.html', context)

class ContactPageView(TemplateView):
    template_name = 'news/contact.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        context = {
            'form' : form
        }
        return render(request, 'news/contact.html', context)

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if  request.method == "POST" and form.is_valid():
            form.save()
            return HttpResponse("<h2> Biz bilan bog'langaningiz uchun tashakkur</h2>")
        context = {
            'form':form
        }

        return request(request, 'news/contact.html', context)

def page404View(request):
    context = {

    }
    return render(request, 'news/404.html', context)

def aboutPageView(request):
    context = {

    }
    return render(request, 'news/about_page.html', context)



class LocalNewsView(ListView):
    model = News
    template_name = 'news/mahalliy.html'
    context_object_name = 'mahalliy_yangiliklar'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name='Mahalliy')
        return news

class SportNewsView(ListView):
    model = News
    template_name = 'news/sport.html'
    context_object_name = 'sport_yangiliklar'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name='Sport')
        return news

class ForeignNewsView(ListView):
    model = News
    template_name = 'news/horij.html'
    context_object_name = 'horij_yangiliklar'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name='Horij')
        return news

class TechnologyNewsView(ListView):
    model = News
    template_name = 'news/texnologiya.html'
    context_object_name = 'texno_yangiliklar'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name='Texnologiya')
        return news

class NewsUpdateView(OnlyLoggedSuperUser, UpdateView):
    model = News
    fields = ('title', 'body', 'image','category','status')
    template_name = 'crud/news_edit.html'

class NewsDeleteView(OnlyLoggedSuperUser, DeleteView):
    model = News
    template_name = 'crud/news_delete.html'
    success_url = reverse_lazy('home_page')

class NewsCreateView(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = News
    template_name = 'crud/news_create.html'
    fields = ('title', 'title_uz', 'title_ru', 'title_en','slug','image','body','body_uz','body_ru','body_en','category','status')
    # success_url = reverse_lazy('home_page')
    prepopulated_fields = {'slug': ('title',)}

    def test_func(self):
        return self.request.user.is_superuser
@user_passes_test(lambda u:u.is_superuser)
@login_required()
def admin_page_view(request):
    admin_users = User.objects.filter(is_superuser=True)

    context = {
        'admin_users' : admin_users
    }
    return render(request,'pages/admin_page.html', context)

class SearchResultsList(ListView):
    model = News
    template_name = 'news/search_result.html'
    context_object_name = 'barcha_yangiliklar'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return News.objects.filter(Q(title__icontains=query) | Q(body__icontains=query))