from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<str:url>', views.redirect_view, name='redirect'),
    path('form/', views.form, name='form'),
    path('my-links/', views.dashboard, name='dashboard'),
    path('edit-link/<int:id>/', views.edit_link, name='edit'),
    path('delete-link/<int:id>/', views.delete_link, name='delete'),
    path('generate-qr/<int:id>/', views.generate_qr, name='generate-qr')
]