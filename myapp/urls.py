from django.urls import path
from . import views

urlpatterns = [
    path('', views.table_list, name='table_list'),
    path('create/', views.create_table, name='create_table'),
    path('edit/<int:table_id>/', views.edit_table, name='edit_table'),
    path('save/<int:table_id>/', views.save_table, name='save_table'),
]