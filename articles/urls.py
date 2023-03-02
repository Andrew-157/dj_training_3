from django.urls import path
from . import views


app_name = 'articles'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('publish/', views.publish_article, name='publish-article'),
    path('personal/<int:user_id>/', views.personal, name='personal-page'),
    path('personal/<int:user_id>/<int:article_id>/',
         views.personal_article, name='personal-article'),
    path('personal/<int:user_id>/<int:article_id>/delete/',
         views.delete_article, name='delete-article'),
    path('personal/<int:user_id>/<int:article_id>/update/',
         views.update_article, name='update-article'),
    path('public/', views.public, name='public')
]
