from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import News, Category
from .forms import ContactForm
from django.views.generic import TemplateView, ListView

# Create your views here.

def news_list(request):
    news_list = News.published.all()
    context = {
        'news_list' : news_list
    }

    return render(request, 'news/news_list.html', context)

def news_detail(request, news):
    news = get_object_or_404(News, slug= news, status = News.Status.Published)
    context = {
        "news" : news
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