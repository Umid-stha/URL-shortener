from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ShortUrl, QRCode
from django.utils import timezone
from .service import create_QR_code
from django.http import HttpResponsePermanentRedirect
from django.db.models import Q, Sum
from django.core.files import File
from django.urls import reverse
import logging

logger = logging.getLogger('__name__')

def home(request):
    if request.method == 'POST':
        long_url = request.POST.get('long_url')
        return render(request, 'shortener/linkForm.html', {'url': long_url})
    return render(request, 'shortener/home.html')

@login_required
def form(request):
    if request.method == 'POST':
        long_url = request.POST.get('long_url')
        custom_short_url = request.POST.get('custom_short_url', None)
        expiration_date = request.POST.get('expiration_date', None)
        generate_QR = request.POST.get('generate_qr')
        created_by = request.user
        try:
            link = ShortUrl.objects.create(
                original_link=long_url,
                created_by=created_by
                )
            if custom_short_url:
                if ShortUrl.objects.filter(custom_short_url=custom_short_url).exists():
                    raise Exception("Custom url already taken")
                else:
                    link.custom_short_url = custom_short_url
            if expiration_date:
                link.expiration_date = expiration_date
            if generate_QR=='on':
                qr_filename, buffer = create_QR_code(link.shortend_link(), link.short_url)
                buffer.seek(0)
                link.qr_code.save(qr_filename, File(buffer), save=False)
            link.save()
            return redirect('result', id=link.id)
        except Exception as e:
            link.delete()
            logger.error(str(e))
            return render(request, 'shortener/linkForm.html', {'error': str(e)})
    return render(request, 'shortener/linkForm.html')

@login_required
def generate_qr_for_short_url(request, id):
    link = get_object_or_404(ShortUrl, id=id)
    qr_filename, buffer = create_QR_code(link.shortend_link(), link.short_url)
    buffer.seek(0)
    link.qr_code.save(qr_filename, File(buffer), save=False)
    link.save()
    return render(request, 'shortener/results.html', {'result': link})
    
@login_required
def dashboard(request):
    today = timezone.now().date()
    links = ShortUrl.objects.filter(created_by = request.user).order_by('-updated_at')
    total_clicks = links.aggregate(Sum('clicks'))['clicks__sum'] or 0
    active_links = links.filter(Q(expiration_date__gte=today) | Q(expiration_date__isnull=True)).count()
    
    context = {
        'links': links,
        'total_clicks': total_clicks,
        'active_links': active_links

    }
    return render(request, 'shortener/dashboard.html', context)

@login_required
def edit_link(request, id):
    link = get_object_or_404(ShortUrl, id=id)
    if request.method == "POST":
        try:
            long_url = request.POST.get('long_url')
            custom_short_url = request.POST.get('custom_short_url', None)
            expiration_date = request.POST.get('expiration_date', None)
            generate_QR = request.POST.get('generate_qr')
            link.original_link = long_url
            if custom_short_url and custom_short_url != link.custom_short_url:
                if ShortUrl.objects.filter(custom_short_url=custom_short_url).exists():
                    raise Exception("Custom url is already in use please choose another one.")
                else:
                    link.custom_short_url = custom_short_url
            if expiration_date:
                link.expiration_date = expiration_date
            if generate_QR=='on':
                qr_filename, buffer = create_QR_code(link.shortend_link(), link.short_url)
                buffer.seek(0)
                link.qr_code.save(qr_filename, File(buffer), save=False)
            link.save()
            url = reverse('result', kwargs={'id': link.id}) + "?edit=true"
            return redirect(url)
        except Exception as e:
            return render(request, 'shortener/editForm.html', {'link': link, 'error': str(e)})
    else:
        return render(request, 'shortener/editForm.html', {'link': link})

@login_required
def delete_link(request, id):
    link = get_object_or_404(ShortUrl, id=id)
    link.delete()
    return redirect('dashboard')

@login_required
def result(request, id):
    link = ShortUrl.objects.get(id=id)
    edit = request.GET.get('edit', False)
    return render(request, 'shortener/results.html', {'result': link, 'edit': edit})

def redirect_view(request, url):
    today = timezone.now().date()
    try:
        redirect_website = ShortUrl.objects.filter(Q(custom_short_url = url) | Q(short_url = url)).first()
        if not redirect_website:
            return render(request, 'shortener/notfound.html', {'error': 'Link not found'}, status=404)
        if not redirect_website.expiration_date or redirect_website.expiration_date >= today:
            redirect_website.clicks += 1
            redirect_website.save()
            return HttpResponsePermanentRedirect(redirect_website.original_link)
        else:
            return render(request, 'shortener/notfound.html', {'error': 'Link already expired'}, status=410)
    except Exception as e:
        return render(request, 'shortener/notfound.html', {'error': str(e)})

#QR code generator page
@login_required
def qr_code_generator(request):
    if request.method == "POST":
        try:
            data = request.POST.get('data')
            name, buffer = create_QR_code(data, data[10:20])
            instance = QRCode.objects.create(data=data, created_by=request.user)
            buffer.seek(0)
            instance.qr_code.save(name, File(buffer), save=True)
            logger.info(f"QR code generated for {data}")
            return redirect('qr-result', id=instance.id)
        except Exception as e:
            logger.error(f"❌ QR generation failed for reason : {e}", exc_info=True)
    return render(request, 'shortener/qrgen.html')

@login_required
def qr_result(request, id):
    qr = QRCode.objects.get(id=id)
    return render(request, 'shortener/qrresult.html', {'result': qr})

@login_required
def qr_history(request):
    qr_codes = QRCode.objects.filter(created_by = request.user).order_by('-created_at')
    return render(request, 'shortener/qrhistory.html', {'qr_codes': qr_codes})

@login_required
def delete_qr(request, id):
    qr = get_object_or_404(QRCode, id=id)
    qr.delete()
    return redirect('qr-history')