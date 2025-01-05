from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BarcodeConfig(AppConfig):
    name = "apps.barcode"
    verbose_name = _("barcode")

