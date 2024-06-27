from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.core.files.uploadedfile import TemporaryUploadedFile


UNITS = {'k': 1000, 'm': 1000_000, 'g': 1000_000_000}


def readableToInt(limit: str) -> int:
    x = limit.lower().rstrip(' ib')  # KiB & KB -> k
    multiply = UNITS.get(x[-1], 1)
    value = float(x.rstrip(' _kmg').replace(',', '.'))
    return int(value * multiply)


@deconstructible
class MaxFilesizeValidator(BaseValidator):
    message = _('File size too large (max. %(limit_value)s).')
    code = 'max_filesize'

    def compare(self, a: TemporaryUploadedFile, limit: str):
        return a.size > readableToInt(limit)
