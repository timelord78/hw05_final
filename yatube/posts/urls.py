from django.conf.urls import handler404, handler500
from django.urls import path

from . import views

handler404 = views.page_not_found
handler500 = views.server_error

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_post, name='group'),
    path('new/', views.new_post, name='new_post'),
    path('follow/', views.follow_index, name='follow_index'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/', views.post_edit, name='edit'),
    path('<str:username>/<int:post_id>/comment/',
         views.add_comment, name="add_comment"),
    path("<str:username>/follow/",
         views.profile_follow, name="profile_follow"),
    path("<str:username>/unfollow/", views.profile_unfollow,
         name="profile_unfollow"),
    path('<str:username>/', views.profile, name='profile'),
]
