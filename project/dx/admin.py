from django.contrib import admin

from .models import Spot, Operator, QSO, Entity, Band, Prefix, OperatorConfirmedPrefix, Filter

admin.site.register(Spot)
admin.site.register(Operator)
admin.site.register(QSO)
admin.site.register(Entity)
admin.site.register(Prefix)
admin.site.register(OperatorConfirmedPrefix)
admin.site.register(Band)
admin.site.register(Filter)
