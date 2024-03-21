from django.urls import path
from django.conf.urls import url
from connected import views
from .views import home_view 
from .views import hub_view, add_tab
from .views import CustomLoginView
from .views import profile_view
from .views import hub_view, tab_detail_view

app_name = 'connected'

urlpatterns = [
    path('', home_view, name='home'),
    path('about/', views.about, name='about'),
    path('category/<slug:category_name_slug>/', views.show_category, name='show_category'),
    path('add_category/', views.add_category, name='add_category'),
    path('category/<slug:category_name_slug>/add_page/', views.add_event, name='add_page'),
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name="login"),
    path('restricted/', views.restricted, name='restricted'),
    path('logout/', views.user_logout, name='logout'),
    path('hub/', views.hub_view, name='hub'),
    path('add_tab/', views.add_tab, name='add_tab'),
    path('profile/', views.profile_view, name='profile'),
    path('tabs/<int:tab_id>/', views.tab_detail_view, name='tab_detail'),
    path('tabs/<int:tab_id>/rename/', views.rename_tab, name='rename_tab'),
    path('tabs/<int:tab_id>/delete/', views.delete_tab, name='delete_tab'),
    path('friends/', views.friends_list, name='friends_list'),
    path('send-message/<int:receiver_id>/', views.send_message, name='send_message'),
    path('friends/add/', views.add_friend, name='add_friend'),
    path('friends/handle_request/', views.handle_friend_request, name='handle_friend_request'),


]