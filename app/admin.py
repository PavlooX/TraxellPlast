from django.contrib import admin
from .models import *


admin.site.register(User)
admin.site.register(Material)
admin.site.register(Color)
admin.site.register(Product)
admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Message)