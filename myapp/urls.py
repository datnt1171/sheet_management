from django.urls import path
from django.contrib.auth import views as auth_views
from myapp import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.index, name='index'),
    path('create/', views.create_table, name='create_table'),
    path('edit/<int:table_id>/', views.edit_table, name='edit_table'),
    path('api/save/<int:table_id>/', views.save_table, name='save_table'),
    path('api/save_consumption/<int:table_id>/', views.save_table_with_consumption, name='save_table_with_consumption'),
]
