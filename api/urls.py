from . import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'api'
urlpatterns= [
    # authentication
    path('',views.registration_view,name='userS'),
    path('check_network/',views.confirmNetwork, name='confirm_network'),
    path('verify/',views.verify_user, name='user_verification'),
    path('reverify/',views.re_verification, name = 'reverification'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name = 'logout'),
    path('user_delete/', views.userDelete_view, name='user_delete'),
    path('user_update/', views.user_update_view, name='user_update'),
    # fetching
    path('category/',views.category_view,name='category'),
    path('concert_favorites/',views.concert_favorite_view,name='favorites'),
    path('service_favorites/',views.service_favorite_view,name='favorites'),
    #create,update and delete
    path('concert_create/', views.concert_create_post,name='create'),
    path('concert_update/',views.concert_update_post, name='update'),
    path('service_create/', views.service_create_post,name='create'),
    path('favorite_create/',views.add_to_favorite,name='category_create'),
    path('service_update/',views.service_update_post, name='update'),
    path('delete/',views.all_delete, name='delete_any'),
    # other functionalities
    # request service and ticketing
    path('request_send/', views.request_send,name='send_request'),
    path('complaint_send/', views.complaint_send,name='send_complaint'),
    path('view_notifications/',views.get_user_requests, name = 'get_requests'),
    path('ticketing/', views.get_ticket,name='ticketing'),
    # search functionality
    path('search_concert/', views.SearchConcerts.as_view(),name='search_concert'),
    path('search_service/', views.SearchServices.as_view(),name='search_service'),
    #view account posted concerts and services
    path('user_posts/',views.account_posts,name = 'user_ads'),
    # view counts
    path('feed_back/',views.confirmFeedBack, name = 'feed_back'),
]

urlpatterns= format_suffix_patterns(urlpatterns)