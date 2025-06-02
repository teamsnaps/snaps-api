from django.contrib import admin

# Register your models here.
from snapsapi.apps.users.models import User

admin.site.register(User)