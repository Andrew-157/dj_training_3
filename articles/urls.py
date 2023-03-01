from django.urls import path
from . import views


app_name = 'articles'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('publish/', views.publish_article, name='publish-article'),
    path('users/<int:user_id>', views.personal, name='personal-page')
]
