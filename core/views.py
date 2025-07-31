from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Warga, Iuran, Pembayaran
from .forms import PembayaranForm
from django.views.decorators.http import require_POST
from django.db.models import Sum
from datetime import datetime

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Arahkan berdasarkan role
            if user.is_superuser:
                return redirect('/admin/')  # Langsung ke admin site
            elif user.groups.filter(name='Bendahara').exists():
                return redirect('dashboard')
            elif user.groups.filter(name='Warga').exists():
                return redirect('dashboard')
            else:
                messages.error(request, 'Role pengguna tidak dikenali.')
                return redirect('login')  # atau redirect('dashboard')
        else:
            messages.error(request, 'Username atau password salah.')
    
    return render(request, 'login.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Username atau password salah')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    if user.role == 'admin':
        return redirect('/admin/')  # langsung ke Django admin
    elif user.role == 'bendahara':
        return redirect('bendahara_dashboard')  # ini akan dibuat
    elif user.role == 'warga':
        return redirect('warga_iuran')
    else:
        return redirect('login')

@login_required
def warga_iuran_view(request):
    if request.user.role != 'warga':
        return redirect('dashboard')

    warga = get_object_or_404(Warga, user=request.user)
    semua_iuran = Iuran.objects.all()
    pembayaran_saya = Pembayaran.objects.filter(warga=warga)
    iuran_terbayar_ids = pembayaran_saya.values_list('iuran__id', flat=True)

    context = {
        'iuran_list': semua_iuran,
        'pembayaran_saya': pembayaran_saya,
        'iuran_terbayar_ids': iuran_terbayar_ids,
        'form': PembayaranForm()
    }
    return render(request, 'warga/iuran.html', context)

@login_required
def unggah_bukti_view(request, iuran_id):
    if request.user.role != 'warga':
        return redirect('dashboard')

    warga = get_object_or_404(Warga, user=request.user)
    iuran = get_object_or_404(Iuran, id=iuran_id)

    if request.method == 'POST':
        form = PembayaranForm(request.POST, request.FILES)
        if form.is_valid():
            pembayaran = form.save(commit=False)
            pembayaran.warga = warga
            pembayaran.iuran = iuran
            pembayaran.save()
            messages.success(request, 'Bukti pembayaran berhasil dikirim. Tunggu konfirmasi dari bendahara.')
            return redirect('warga_iuran')
    else:
        form = PembayaranForm()

    return render(request, 'warga/unggah_bukti.html', {'form': form, 'iuran': iuran})

@login_required
def bendahara_dashboard_view(request):
    if request.user.role != 'bendahara':
        return redirect('dashboard')

    pembayaran_belum_dikonfirmasi = Pembayaran.objects.filter(dikonfirmasi=False)
    pembayaran_terkonfirmasi = Pembayaran.objects.filter(dikonfirmasi=True)

    context = {
        'belum_dikonfirmasi': pembayaran_belum_dikonfirmasi,
        'terkonfirmasi': pembayaran_terkonfirmasi
    }
    return render(request, 'bendahara/dashboard.html', context)

@require_POST
@login_required
def konfirmasi_pembayaran_view(request, pembayaran_id):
    if request.user.role != 'bendahara':
        return redirect('dashboard')

    pembayaran = get_object_or_404(Pembayaran, id=pembayaran_id)
    pembayaran.dikonfirmasi = True
    pembayaran.save()

    # Simpan notifikasi hanya di session bendahara
    if request.user.is_authenticated:
        messages.success(request, 'Pembayaran berhasil dikonfirmasi.')

    return redirect('bendahara_dashboard')


@login_required
def laporan_bulanan_view(request):
    if request.user.role != 'bendahara':
        return redirect('dashboard')

    bulan = request.GET.get('bulan', datetime.now().month)
    tahun = request.GET.get('tahun', datetime.now().year)

    pembayaran = Pembayaran.objects.filter(
        tanggal_bayar__month=bulan,
        tanggal_bayar__year=tahun,
        dikonfirmasi=True
    )

    total_pemasukan = pembayaran.aggregate(total=Sum('iuran__jumlah'))['total'] or 0

    context = {
        'pembayaran': pembayaran,
        'total_pemasukan': total_pemasukan,
        'bulan': int(bulan),
        'tahun': int(tahun),
    }

    return render(request, 'bendahara/laporan.html', context)


@login_required
def warga_riwayat_view(request):
    warga = get_object_or_404(Warga, user=request.user)
    pembayaran_list = Pembayaran.objects.filter(warga=warga).order_by('-tanggal_bayar')
    return render(request, 'warga/riwayat_pembayaran.html', {'pembayaran_list': pembayaran_list})