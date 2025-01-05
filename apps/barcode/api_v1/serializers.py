
# from PIL import Image
# from reportlab.pdfgen import canvas
# from barcode import Code128
# from barcode.writer import ImageWriter
# from io import BytesIO
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.exceptions import ValidationError
# from django.core.files.storage import default_storage
# import os
# from django.conf import settings
# import base64
# from apps.item.models import StockItem


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def generate_barcode(request):

#     item_code = request.data.get("item_code")
#     item_name = request.data.get("name", "Unknown_Item")
#     selling_price = request.data.get("selling_price", "N/A")
#     organization_name = request.data.get("organization_name", "Unknown_Organization")
#     barcode_field = request.data.get("barcode", item_code)

#     if not barcode_field:
#         raise ValidationError({"error": "Barcode value is required"})

#     try:
#         barcode = Code128(barcode_field, writer=ImageWriter())
#         barcode_buffer = BytesIO()
#         barcode.write(barcode_buffer)
#         barcode_buffer.seek(0)
#         barcode_image = Image.open(barcode_buffer)
#         barcode_image_path = os.path.join(settings.MEDIA_ROOT, "temp_barcode.png")
#         barcode_image.save(barcode_image_path, format="PNG")
#         pdf_buffer = BytesIO()
#         c = canvas.Canvas(pdf_buffer)
#         c.setFont("Helvetica-Bold", 14)
#         c.drawString(100, 750, f"Organization: {organization_name}")
#         c.drawString(100, 720, f"Item Name: {item_name}")
#         c.drawString(100, 690, f"Selling Price: {selling_price}")
#         c.drawString(100, 660, f"Item Code: {item_code}")
#         c.drawInlineImage(barcode_image_path, 100, 600, width=200, height=50)


#         c.save()
#         pdf_buffer.seek(0)

#         pdf_directory = os.path.join(settings.MEDIA_ROOT, "barcodes")
#         os.makedirs(pdf_directory, exist_ok=True)
#         pdf_filename = f"{organization_name}_{item_name}.pdf".replace(" ", "_")
#         pdf_path = os.path.join(pdf_directory, pdf_filename)

#         with default_storage.open(pdf_path, "wb") as pdf_file:
#             pdf_file.write(pdf_buffer.getvalue())

#         pdf_url = request.build_absolute_uri(f"{settings.MEDIA_URL}barcodes/{pdf_filename}")

#         return Response({
#             "status": 1,
#             "message": "Barcode and PDF generated successfully.",
#             "item_code": item_code,
#             "item_name": item_name,
#             "selling_price": selling_price,
#             "organization_name": organization_name,
#             "barcode_value": barcode_field,
#             "pdf_url": pdf_url
#         })

#     except Exception as e:
#         return Response({"status": 0, "error": str(e)})

from rest_framework import serializers

# Placeholder Serializer
class BarcodePrintSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=True)
    barcode = serializers.CharField(max_length=128)
    selectedCheckboxes = serializers.DictField(child=serializers.BooleanField(), required=False)

