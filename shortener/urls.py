from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<str:url>', views.redirect_view, name='redirect'),
    path('form/', views.form, name='form'),
    path('my-links/', views.dashboard, name='dashboard'),
    path('result/<int:id>/', views.result, name='result'),
    path('qr-result/<int:id>/', views.qr_result, name='qr-result'),
    path('edit-link/<int:id>/', views.edit_link, name='edit'),
    path('delete-link/<int:id>/', views.delete_link, name='delete'),
    path('generate-qr/<int:id>/', views.generate_qr_for_short_url, name='generate-qr'),
    path('qr-gen/', views.qr_code_generator, name='qr-gen'),
    path('qr-history/', views.qr_history, name='qr-history'),
    path('delete-qr/<int:id>/', views.delete_qr, name='delete-qr'),
]