# sporttrack_project/urls.py
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from core.views import (
    home_view,
    register_view,
    create_group_view,
    list_groups_view,
    join_group_view,
    group_detail_view,
    add_activity_view,
    leave_group_view,
    custom_logout_view,  # Custom logout
)

urlpatterns = [
    # Admin rotası
    path('admin/', admin.site.urls),

    # Ana sayfa
    path('', home_view, name='home'),

    # Kayıt
    path('register/', register_view, name='register'),

    # Hazır login/logout rotaları
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),

    # Custom logout rotası ( logout)
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Gruplar
    path('groups/', list_groups_view, name='list_groups'),
    path('groups/create/', create_group_view, name='create_group'),
    path('groups/join/<int:group_id>/', join_group_view, name='join_group'),
    path('groups/<int:group_id>/', group_detail_view, name='group_detail'),

    # Aktivite ekleme
    path('activities/add/', add_activity_view, name='add_activity'),
    path('groups/<int:group_id>/', group_detail_view, name='group_detail'),

    path('groups/leave/<int:group_id>/', leave_group_view, name='leave_group'),

]
