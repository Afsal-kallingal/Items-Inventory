from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.urls import path, include
from apps.barcode.api_v1.views import generate_barcode,barcode_print_view
# from apps.barcode.api_v1.serializers import BaaaaaarcodePrintViewSet
if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

urlpatterns = [
    path('barcode/', generate_barcode, name='generate_barcode'), 
    path('print-barcode/', barcode_print_view, name='print_barcode'),
    # path('advanced-barcode/', generate_barcode_from_item_id, name='advanced_generate_barcode'),

]

# router.register('barcode-print', BarcodePrintViewSet, basename='barcode-print')
# router.register('barcode-print-test', BarcodePrintViewSetsss, basename='barcode-ssprint')
# router.register('test-print', BaaaaaarcodePrintViewSet, basename='barcode-test-print')

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "api_v1"


