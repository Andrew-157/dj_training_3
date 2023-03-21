from django.urls import path
from django.views.generic import TemplateView
from . import views


app_name = 'articles'
urlpatterns = [
    path('', TemplateView.as_view(
        template_name='articles/index.html'), name='index'),
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('publish/', views.PublishArticle.as_view(), name='publish-article'),
    path('personal/', views.personal_page, name='personal-page'),
    path('personal/<int:article_id>/',
         views.personal_article, name='personal-article'),
    path('personal/<int:article_id>/delete/',
         views.delete_article, name='delete-article'),
    path('personal/<int:article_id>/comment/',
         views.author_comment, name='author-comment'),
    path('personal/<int:article_id>/update/',
         views.update_article, name='update-article'),
    path('public/', views.public_page, name='public'),
    path('public/<int:article_id>/', views.public_article, name='public-article'),
    path('public/<int:article_id>/comment/',
         views.leave_comment, name='leave-comment'),
    path('become_user/', TemplateView.as_view(template_name='articles/become_user.html'),
         name='become-user'),
    path('public/<int:article_id>/like/', views.leave_like, name='like'),
    path('public/<int:article_id>/dislike/',
         views.leave_dislike, name='dislike'),
    path('public/tags/trending/', views.trending_tags, name='trending-tags'),
    path('public/tags/<str:tag>/', views.articles_through_tag, name='articles-tag'),
    path('public/search-article/', views.search_article,
         name='search-article'),
    path('public/articles/trending/',
         views.trending_articles, name='trending-articles'),
    path('public/authors/<str:author>/',
         views.author_page, name='articles-author'),
    path('public/authors/<str:author>/subscribe/',
         views.subscribe, name='subscribe')
]
