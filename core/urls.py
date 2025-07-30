from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('warga/iuran/', views.warga_iuran_view, name='warga_iuran'),
    path('warga/upload/<int:iuran_id>/', views.unggah_bukti_view, name='unggah_bukti'),
]
