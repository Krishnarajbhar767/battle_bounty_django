from django.contrib import admin
from  .models import Tournament,GameProfile,Team
# Register your models here.
admin.site.register(Tournament)
admin.site.register(GameProfile)
admin.site.register(Team)
