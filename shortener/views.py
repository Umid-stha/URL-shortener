from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ShortUrl
from django.utils import timezone
from .service import create_QR_code
from django.http import HttpResponsePermanentRedirect
from django.db.models import Q, Sum
from django.core.files import File

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
                    return render(request, 'shortener/linkForm.html', {'error': 'This custom short URL is already taken.'})
                else:
                    link.custom_short_url = custom_short_url
            if expiration_date:
                link.expiration_date = expiration_date
            if generate_QR=='on':
                qr_filename, buffer = create_QR_code(link.shortend_link())
                link.qr_code.save(qr_filename, File(buffer), save=False)
            link.save()
            return render(request, 'shortener/results.html', {'result': link})
        except Exception:
            return render(request, 'shortener/linkForm.html', {'error': 'An error occurred. Please try again later.'})
    return render(request, 'shortener/linkForm.html')

@login_required
def generate_qr(request, id):
    link = get_object_or_404(ShortUrl, id=id)
    qr_filename, buffer = create_QR_code(link.shortend_link())
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
    pass

@login_required
def delete_link(request, id):
    link = get_object_or_404(ShortUrl, id=id)
    link.delete()
    return redirect('dashboard')

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