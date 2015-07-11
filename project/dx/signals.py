from django.db.models.signals import post_save
from django.dispatch import receiver

from dx.models import Operator, Prefix, QSO, OperatorConfirmedPrefix

from drafts import colors
 
@receiver(post_save, sender=QSO)
def add_confirmed_qso(sender, **kwargs):
    instance = kwargs['instance']
    
    if instance.is_confirmed():
        prefix = instance.prefix
        operator = instance.operator

        ocp, created = OperatorConfirmedPrefix.objects.get_or_create(
            prefix=prefix,
            operator=operator,
        )
