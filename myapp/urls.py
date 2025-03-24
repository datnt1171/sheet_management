from django.urls import path
from . import views

urlpatterns = [
    path('', views.table_list, name='table_list'),
    path('create/', views.create_table, name='create_table'),
    path('edit/<int:table_id>/', views.edit_table, name='edit_table'),
    path('api/save/<int:table_id>/', views.save_table, name='save_table'),
    path('api/save-with-temp-name/<int:table_id>/', views.save_table_with_temp_name, name='save_table_with_temp_name'),
]