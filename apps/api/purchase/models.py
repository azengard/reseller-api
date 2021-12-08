from django.db import models


class Purchase(models.Model):
    class PurchaseStatus(models.TextChoices):
        VALIDATING = 'validating', "Em validação"
        APPROVED = 'approved', "Aprovado"
        REPROVED = 'reproved', "Reprovado"

    reseller_cpf = models.ForeignKey('reseller.Reseller', related_name='purchases', on_delete=models.CASCADE,
                                     to_field='cpf')
    code = models.CharField(max_length=10)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    status = models.CharField(max_length=max(map(len, PurchaseStatus.values)),
                              choices=PurchaseStatus.choices, default=PurchaseStatus.VALIDATING)
