from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Bendahara Dashboard dan fitur terkait
    path('bendahara/dashboard/', views.bendahara_dashboard_view, name='bendahara_dashboard'),

    # CRUD Iuran oleh Bendahara
    path('bendahara/iuran/', views.iuran_list_view, name='iuran_list'),
    path('bendahara/iuran/tambah/', views.iuran_add_view, name='iuran_add'),
    path('bendahara/iuran/edit/<int:iuran_id>/', views.iuran_edit_view, name='iuran_edit'),
    path('bendahara/iuran/hapus/<int:iuran_id>/', views.iuran_delete_view, name='iuran_delete'),

    path('bendahara/tambah_pembayaran/', views.tambah_pembayaran_view, name='tambah_pembayaran'),
    path('bendahara/konfirmasi/<int:pembayaran_id>/', views.konfirmasi_pembayaran_view, name='konfirmasi_pembayaran'),
    path('bendahara/transaksi/<str:blok_rumah>/', views.cari_transaksi_view, name='cari_transaksi'),
    path('bendahara/laporan/', views.laporan_bulanan_view, name='laporan_bulanan'),

    # Admin Dashboard dan fitur terkait
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/tambah_bendahara/', views.tambah_bendahara_view, name='tambah_bendahara'),
]
