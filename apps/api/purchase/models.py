import uuid

from django.db import models


class Purchase(models.Model):
    class PurchaseStatus(models.TextChoices):
        VALIDATING = 'validating'
        APPROVED = 'approved'
        REPROVED = 'reproved'

    purchase_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    reseller_cpf = models.ForeignKey('reseller.Reseller', related_name='purchases', on_delete=models.CASCADE,
                                     to_field='cpf')
    code = models.CharField(max_length=10)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    status = models.CharField(max_length=max(map(len, PurchaseStatus.values)),
                              choices=PurchaseStatus.choices, default=PurchaseStatus.VALIDATING)

    def get_cashback_percentage(self):
        value = float(self.value)
        if value <= 1000:
            percentage = 10.0
        elif value <= 1500:
            percentage = 15.0
        else:
            percentage = 20.0
        return percentage

    def get_cashback_value(self):
        percentage = self.get_cashback_percentage()
        cashback_value = (float(self.value) * percentage) / 100
        return cashback_value
