from . import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'api'
urlpatterns= [
    # authentication
    path('',views.registration_view,name='userS'),
    path('verify/',views.verify_user, name='user_verification'),
    path('reverify/',views.re_verification, name = 'reverification'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name = 'logout'),
    path('user_delete/', views.userDelete_view, name='user_delete'),
    path('user_update/', views.user_update_view, name='user_update'),
    path('category/',views.category_view,name='category'),
    path('concert_create/', views.concert_create_post,name='create'),
    path('concert_update/',views.concert_update_post, name='update'),
    path('service_create/', views.service_create_post,name='create'),
    path('service_update/',views.service_update_post, name='update'),
    path('request_send/', views.request_send,name='send_request'),
    path('ticketing/', views.ticketing,name='ticketing'),
    path('delete/',views.all_delete, name='delete_any'),
]

urlpatterns= format_suffix_patterns(urlpatterns)