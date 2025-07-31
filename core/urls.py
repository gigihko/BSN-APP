from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('warga/iuran/', views.warga_iuran_view, name='warga_iuran'),
    path('warga/upload/<int:iuran_id>/', views.unggah_bukti_view, name='unggah_bukti'),
    path('warga/riwayat/', views.warga_riwayat_view, name='warga_riwayat'),


    path('bendahara/dashboard/', views.bendahara_dashboard_view, name='bendahara_dashboard'),
    path('bendahara/konfirmasi/<int:pembayaran_id>/', views.konfirmasi_pembayaran_view, name='konfirmasi_pembayaran'),
    path('bendahara/laporan/', views.laporan_bulanan_view, name='laporan_bulanan'),

]
