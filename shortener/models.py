from django.db import models
from django.contrib.auth import get_user_model
import string
from django.conf import settings

AVAILABLE_CHARACTERS = string.ascii_letters + string.digits

def encode_base62(id):
    encoded_chars=[]
    while id > 0:
        r = id % 62
        id = (id - r)/62
        encoded_chars.append(AVAILABLE_CHARACTERS[r])
    return ''.join(reversed(encoded_chars)) or '0'

def get_absolute_url(url_string: string):
    if url_string.startswith('/'):
        return settings.WEBSITE_URL + url_string
    else:
        return settings.WEBSITE_URL + '/' + url_string

User = get_user_model()

# Create your models here.
class ShortUrl(models.Model):
    original_link = models.URLField()
    custom_short_url = models.TextField(null=True, blank=True, unique=True, db_index=True)
    short_url = models.CharField(max_length=7, null=True, blank=True, unique=True, db_index=True)

    expiration_date = models.DateField(null=True, blank=True)
    clicks = models.IntegerField(default=0)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    qr_code = models.ImageField(upload_to='images/shortQR/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.short_url:
            self.short_url = encode_base62(self.id)
            super().save(update_fields=['short_url'])

    #get full link along with short part
    def shortend_link(self):
        if not self.custom_short_url:
            return get_absolute_url(self.short_url)
        else:
            return get_absolute_url(self.custom_short_url)
        
    def qr_code_url(self):
        return get_absolute_url(self.qr_code.url)

class QRCode(models.Model):
    #link, text, data, etc turning into qr
    data = models.TextField()
    qr_code = models.ImageField(upload_to='images/QRcodes/', null=True, blank=True)

    created_by=models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def qr_code_url(self):
        return get_absolute_url(self.qr_code.url)

