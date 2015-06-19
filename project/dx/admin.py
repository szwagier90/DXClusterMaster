from django.contrib import admin

from .models import Spot, Operator, QSO, Entity

admin.site.register(Spot)
admin.site.register(Operator)
admin.site.register(QSO)
admin.site.register(Entity)
