from django.contrib import admin
from tracker.models import Category, Transaction

# khi dang ki 1 model, django tu tao trang quan ly cho model do trong Admin site
# Register your models here.
admin.site.register(Transaction)
admin.site.register(Category)
