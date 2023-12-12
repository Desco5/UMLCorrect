import os
from django.core.exceptions import ValidationError

def validate_mdj(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".mdj"]
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')
    return value

def validate_excel(value):
    #TODO Missing validation for format and content of the "excel" file

    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".xlsx",".xls",".xlsm",".xlsb",".odf",".ods",".odt"]
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')
    return value