from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('bendahara', 'Bendahara'),
        ('warga', 'Warga'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    alamat = models.TextField(blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Warga(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    no_rumah = models.CharField(max_length=10)
    rt = models.CharField(max_length=3, default="01")  # Opsional

    def __str__(self):
        return f"{self.user.username} - No. {self.no_rumah}"

class Iuran(models.Model):
    JENIS_CHOICES = [
        ('sampah', 'Iuran Sampah'),
        ('kas', 'Kas RT'),
        ('keamanan', 'Keamanan'),
        ('lain', 'Lainnya'),
    ]
    nama = models.CharField(max_length=100)
    jenis = models.CharField(max_length=20, choices=JENIS_CHOICES)
    jumlah = models.PositiveIntegerField()
    tanggal_ditambahkan = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama} - Rp{self.jumlah}"

class Pembayaran(models.Model):
    METODE_CHOICES = [
        ('tunai', 'Tunai'),
        ('transfer', 'Transfer'),
        ('qris', 'QRIS'),
    ]

    warga = models.ForeignKey('Warga', on_delete=models.CASCADE)
    iuran = models.ForeignKey('Iuran', on_delete=models.CASCADE)
    tanggal_bayar = models.DateField(auto_now_add=True)
    metode = models.CharField(max_length=20, choices=METODE_CHOICES)
    bukti_transfer = models.ImageField(upload_to='bukti/', blank=True, null=True)
    dikonfirmasi = models.BooleanField(default=False)
    keterangan = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.warga} bayar {self.iuran.nama} via {self.get_metode_display()}"
