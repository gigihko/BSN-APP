from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Warga, Iuran, Pembayaran, User
from django.views.decorators.http import require_POST
from django.db.models import Sum
from datetime import datetime

# --- Halaman depan untuk warga, tanpa login ---
def index_view(request):
    """
    Halaman utama warga, menampilkan rekap iuran dan pembayaran per blok secara umum.
    """
    semua_iuran = Iuran.objects.all()
    pembayaran_terkonfirmasi = Pembayaran.objects.filter(dikonfirmasi=True)

    # Hitung persentase bayar per jenis iuran
    summary = []
    for iuran in semua_iuran:
        total_warga = Warga.objects.count()
        bayar_count = pembayaran_terkonfirmasi.filter(iuran=iuran).values('warga').distinct().count()
        persentase_bayar = (bayar_count / total_warga * 100) if total_warga > 0 else 0
        summary.append({
            'iuran': iuran,
            'persentase_bayar': round(persentase_bayar, 2),
            'total_bayar': bayar_count,
            'total_warga': total_warga,
        })

    context = {
        'summary': summary,
    }
    return render(request, 'index.html', context)

# --- Gabungan login untuk admin & bendahara ---
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_active:
                messages.error(request, 'Akun Anda tidak aktif.')
                return redirect('login')

            login(request, user)

            # Arahkan sesuai role
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'bendahara':
                return redirect('bendahara_dashboard')
            else:
                messages.error(request, 'Role pengguna tidak dikenali.')
                logout(request)
                return redirect('login')
        else:
            messages.error(request, 'Username atau password salah.')

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')  # arahkan ke halaman utama warga

# --- Bendahara Dashboard ---
@login_required
def bendahara_dashboard_view(request):
    if request.user.role != 'bendahara':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    pembayaran_belum = Pembayaran.objects.filter(dikonfirmasi=False)
    pembayaran_sudah = Pembayaran.objects.filter(dikonfirmasi=True)

    context = {
        'belum_dikonfirmasi': pembayaran_belum,
        'terkonfirmasi': pembayaran_sudah,
    }
    return render(request, 'bendahara/dashboard.html', context)

# --- CRUD Iuran untuk Bendahara ---
@login_required
def iuran_list_view(request):
    if request.user.role != 'bendahara':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    iuran_list = Iuran.objects.all()
    return render(request, 'bendahara/iuran_list.html', {'iuran_list': iuran_list})

@login_required
def iuran_add_view(request):
    if request.user.role != 'bendahara':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    if request.method == 'POST':
        nama = request.POST.get('nama')
        jumlah = request.POST.get('jumlah')
        if nama and jumlah:
            Iuran.objects.create(nama=nama, jumlah=jumlah)
            messages.success(request, 'Iuran berhasil ditambahkan.')
            return redirect('iuran_list')
        else:
            messages.error(request, 'Data iuran tidak lengkap.')

    return render(request, 'bendahara/iuran_form.html', {'action': 'Tambah'})

@login_required
def iuran_edit_view(request, iuran_id):
    if request.user.role != 'bendahara':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    iuran = get_object_or_404(Iuran, id=iuran_id)

    if request.method == 'POST':
        nama = request.POST.get('nama')
        jumlah = request.POST.get('jumlah')
        if nama and jumlah:
            iuran.nama = nama
            iuran.jumlah = jumlah
            iuran.save()
            messages.success(request, 'Iuran berhasil diperbarui.')
            return redirect('iuran_list')
        else:
            messages.error(request, 'Data iuran tidak lengkap.')

    return render(request, 'bendahara/iuran_form.html', {'action': 'Edit', 'iuran': iuran})

@login_required
def iuran_delete_view(request, iuran_id):
    if request.user.role != 'bendahara':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    iuran = get_object_or_404(Iuran, id=iuran_id)
    iuran.delete()
    messages.success(request, 'Iuran berhasil dihapus.')
    return redirect('iuran_list')

# --- Tambah Pembayaran (oleh bendahara) ---
@login_required
def tambah_pembayaran_view(request):
    if request.user.role != 'bendahara':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    if request.method == 'POST':
        warga_id = request.POST.get('warga_id')
        iuran_id = request.POST.get('iuran_id')
        metode = request.POST.get('metode')
        keterangan = request.POST.get('keterangan', '')

        warga = get_object_or_404(Warga, id=warga_id)
        iuran = get_object_or_404(Iuran, id=iuran_id)

        Pembayaran.objects.create(
            warga=warga,
            iuran=iuran,
            metode=metode,
            dikonfirmasi=True,  # langsung konfirmasi karena bendahara yang input
            keterangan=keterangan
        )
        messages.success(request, 'Pembayaran berhasil ditambahkan.')
        return redirect('bendahara_dashboard')

    warga_list = Warga.objects.all()
    iuran_list = Iuran.objects.all()
    metode_list = ['tunai', 'transfer']  # QRIS dimatikan sementara

    context = {
        'warga_list': warga_list,
        'iuran_list': iuran_list,
        'metode_list': metode_list,
    }
    return render(request, 'bendahara/tambah_pembayaran.html', context)

# --- Konfirmasi pembayaran ---
@require_POST
@login_required
def konfirmasi_pembayaran_view(request, pembayaran_id):
    if request.user.role != 'bendahara':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    pembayaran = get_object_or_404(Pembayaran, id=pembayaran_id)
    pembayaran.dikonfirmasi = True
    pembayaran.save()
    messages.success(request, 'Pembayaran berhasil dikonfirmasi.')
    return redirect('bendahara_dashboard')

# --- Cari transaksi per blok rumah ---
@login_required
def cari_transaksi_view(request, blok_rumah):
    if request.user.role != 'bendahara':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    warga_blok = Warga.objects.filter(blok=blok_rumah)
    pembayaran = Pembayaran.objects.filter(warga__in=warga_blok).order_by('-tanggal_bayar')

    context = {
        'blok': blok_rumah,
        'pembayaran_list': pembayaran,
    }
    return render(request, 'bendahara/transaksi_per_blok.html', context)

# --- Laporan bulanan ---
@login_required
def laporan_bulanan_view(request):
    if request.user.role != 'bendahara':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    bulan = int(request.GET.get('bulan', datetime.now().month))
    tahun = int(request.GET.get('tahun', datetime.now().year))

    pembayaran = Pembayaran.objects.filter(
        tanggal_bayar__year=tahun,
        tanggal_bayar__month=bulan,
        dikonfirmasi=True
    )

    total_pemasukan = pembayaran.aggregate(total=Sum('iuran__jumlah'))['total'] or 0

    context = {
        'pembayaran': pembayaran,
        'total_pemasukan': total_pemasukan,
        'bulan': bulan,
        'tahun': tahun,
    }
    return render(request, 'bendahara/laporan.html', context)

# --- Admin Dashboard ---
@login_required
def admin_dashboard_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    bendahara_list = User.objects.filter(role='bendahara')

    context = {
        'bendahara_list': bendahara_list,
    }
    return render(request, 'admin/dashboard.html', context)

# --- Tambah Bendahara ---
@login_required
def tambah_bendahara_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Akses ditolak.')
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah ada.')
        else:
            User.objects.create_user(username=username, password=password, role='bendahara')
            messages.success(request, f'Bendahara {username} berhasil dibuat.')
            return redirect('admin_dashboard')

    return render(request, 'admin/tambah_bendahara.html')
