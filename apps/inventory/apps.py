from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class InventoryConfig(AppConfig):
    name = "apps.inventory" 
    verbose_name = _("Inventory")

    # def ready(self):
    #     import apps.inventory.signals
