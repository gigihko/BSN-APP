from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Warga, Iuran, Pembayaran
from .forms import PembayaranForm

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
    