import re

from rest_framework.exceptions import ValidationError


def cpf_validator(value):
    message = 'Invalid CPF'
    cpf_pattern = re.compile(r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$")
    if not cpf_pattern.fullmatch(value):
        raise ValidationError(message)

    cpf = [int(char) for char in value if char.isdigit()]

    if cpf == cpf[::-1]:
        raise ValidationError(message)

    #  Validate last 2 digits
    for i in range(9, 11):
        value = sum((cpf[num] * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != cpf[i]:
            raise ValidationError(message)
