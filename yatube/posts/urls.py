from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),

    # Профайл пользователя
    path('profile/<str:username>/', views.profile, name='profile'),

    # Просмотр постов группы
    path('group/<slug:slug>/', views.group_posts, name='group_list'),

    # Создание записей
    path('create/', views.post_create, name='post_create'),

    # Просмотр записи
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),

    # Редактирование записей
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),

    # Создание комментариев
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),

    # Просмотр личных подписок

    path('follow/', views.follow_index, name='follow_index'),

    # что-то
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),

    # что-то
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
