from PIL import Image
from reportlab.pdfgen import canvas
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.files.storage import default_storage
import os
from datetime import datetime
import pdfkit
from django.conf import settings
import base64
import sys
from apps.item.models import StockItem
from apps.barcode.api_v1.serializers import BarcodePrintSerializer
import cairosvg
from rest_framework import viewsets
from rest_framework.response import Response

# from rest_framework.permissions import IsAuthenticated
from apps.item.models import StockItem

# from io import BytesIO
# import base64
# import os
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


# import sys
from django.conf import settings

# import pdfkit
# from PyPDF2 import PdfReader, PdfWriter
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from barcode.writer import SVGWriter
import logging


logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_barcode(request):
    item_code = request.data.get("item_code")
    item_name = request.data.get("name", "Unknown_Item")
    selling_price = request.data.get("selling_price", "N/A")
    organization_name = request.data.get("organization_name", "Unknown_Organization")
    barcode_field = request.data.get("barcode", item_code)

    if not barcode_field:
        raise ValidationError({"error": "Barcode value is required"})

    try:
        barcode = Code128(barcode_field, writer=ImageWriter())
        barcode_buffer = BytesIO()
        barcode.write(barcode_buffer)
        barcode_buffer.seek(0)
        barcode_image = Image.open(barcode_buffer)
        barcode_image_path = os.path.join(settings.MEDIA_ROOT, "temp_barcode.png")
        barcode_image.save(barcode_image_path, format="PNG")
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 750, f"Organization: {organization_name}")
        c.drawString(100, 720, f"Item Name: {item_name}")
        c.drawString(100, 690, f"Selling Price: {selling_price}")
        c.drawString(100, 660, f"Item Code: {item_code}")
        c.drawInlineImage(barcode_image_path, 100, 600, width=200, height=50)

        c.save()
        pdf_buffer.seek(0)

        pdf_directory = os.path.join(settings.MEDIA_ROOT, "barcodes")
        os.makedirs(pdf_directory, exist_ok=True)
        pdf_filename = f"{organization_name}_{item_name}.pdf".replace(" ", "_")
        pdf_path = os.path.join(pdf_directory, pdf_filename)

        with default_storage.open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_buffer.getvalue())

        pdf_url = request.build_absolute_uri(
            f"{settings.MEDIA_URL}barcodes/{pdf_filename}"
        )

        return Response(
            {
                "status": 1,
                "message": "Barcode and PDF generated successfully.",
                "item_code": item_code,
                "item_name": item_name,
                "selling_price": selling_price,
                "organization_name": organization_name,
                "barcode_value": barcode_field,
                "pdf_url": pdf_url,
            }
        )

    except Exception as e:
        return Response({"status": 0, "error": str(e)})


class CustomSVGWriter(SVGWriter):
    def __init__(self, module_height=15, module_width=5.0):
        super().__init__()
        self.module_height = module_height
        self.module_width = module_width

    def _draw_text(self, text, x, y):
        # Adjust text positioning
        self._svg.text(text, (x + 5, y), fill="black", font_size="2")


class BarcodePrintViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = StockItem.objects.all()

    @method_decorator(csrf_exempt)
    def create(self, request):
        try:
            int_itemid = request.data.get("item_id")
            vchr_barcode = request.data.get("barcode")
            selected_checkboxes = request.data.get("selectedCheckboxes", {})
            selling_price = selected_checkboxes.get("sellingPrice", True)
            company_name = selected_checkboxes.get("companyName", False)
            item_name_flag = selected_checkboxes.get("itemName", False)

            if not int_itemid or not vchr_barcode:
                return Response(
                    {"status": 0, "reason": "Item ID and Barcode number are required."},
                    status=400,
                )

            item = StockItem.objects.filter(id=int_itemid).first()

            if not item:
                return Response({"status": 0, "reason": "Item not found."}, status=404)

            item.barcode = vchr_barcode
            item.save()

            # Generate the barcode as SVG
            code128 = Code128(
                vchr_barcode, writer=CustomSVGWriter(module_height=15, module_width=5.0)
            )
            buffer = BytesIO()
            code128.write(buffer)
            buffer.seek(0)

            # Convert SVG to PNG
            svg_data = buffer.getvalue()
            svg_str = svg_data.decode("utf-8")
            modified_svg_data = svg_str.encode("utf-8")
            png_output = BytesIO()
            cairosvg.svg2png(
                bytestring=modified_svg_data,
                write_to=png_output,
                output_height=2000,
                output_width=1600,
            )
            png_output.seek(0)

            # Encode PNG to base64
            barcode_image_base64 = base64.b64encode(png_output.getvalue()).decode(
                "utf-8"
            )

            dct_data = {
                "barcode_image": f"data:image/png;base64,{barcode_image_base64}",
                "item_id": item.id,
                "item_name": item.name if item_name_flag else "",
                "selling_price": item.selling_price if selling_price else "",
                "company_name": item.organization_id if company_name else "",
                "item_code": item.item_code,
            }

            html_output = barcode_print(dct_data)

            # Save PDF
            file_path = os.path.join(settings.MEDIA_ROOT, "barcodes")
            os.makedirs(file_path, exist_ok=True)
            str_file_name = f"Barcode_Generation-{datetime.now().strftime('%d_%m_%Y_%H_%M_%S_%f')}.pdf"
            pdf_file_path = os.path.join(file_path, str_file_name)

            options = {
                "page-width": "50mm",
                "page-height": "40mm",
                "dpi": 300,
                "disable-smart-shrinking": "",
                "enable-local-file-access": "",
            }

            pdfkit.from_string(html_output, pdf_file_path, options=options)

            # Encode PDF to base64
            with open(pdf_file_path, "rb") as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read()).decode("utf-8")

            str_request_protocol = "https" if request.is_secure() else "http"

            return Response(
                {
                    "status": 1,
                    "file_url": f"{str_request_protocol}://{request.META['HTTP_HOST']}/media/barcodes/{str_file_name}",
                    "dct_data": dct_data,
                    "encoded_pdf": encoded_string,
                }
            )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in BarcodePrintViewSet.create: {e} at line {exc_tb.tb_lineno}"
            )
            return Response(
                {"status": 0, "reason": "An error occurred. Please try again later."},
                status=500,
            )


def barcode_print(dct_data):
    barcode_image = dct_data.get("barcode_image", "")
    item_name = dct_data.get("item_name", "")
    selling_price = dct_data.get("selling_price", "")
    company_name = dct_data.get("company_name", "")

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Barcode Display</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                width: 50mm;
                height: 40mm;
            }}
            .container {{
                width: 100%;
                height: 100%;
                text-align: center;
            }}
            h3 {{
                margin: 0;
                font-size: 10px;
            }}
            p {{
                margin: 0;
                font-size: 12px;
                line-height: 1;
            }}
            img {{
                height: 15mm;
                object-fit: stretch;
                width: 30mm;
                margin-left: -10mm;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h3>{company_name}</h3>
            <img src="{barcode_image}" alt="Generated Barcode" />
            <p>{item_name}</p>
            <p>Selling Price: {selling_price}</p>
        </div>
    </body>
    </html>
    """


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def barcode_print_view(request):
    try:
        int_itemid = request.data.get("item_id")
        vchr_barcode = request.data.get("barcode")
        selected_checkboxes = request.data.get("selectedCheckboxes", {})
        selling_price = selected_checkboxes.get("sellingPrice", True)
        company_name = selected_checkboxes.get("companyName", False)
        item_name_flag = selected_checkboxes.get("itemName", False)

        if not int_itemid or not vchr_barcode:
            return Response(
                {"status": 0, "reason": "Item ID and Barcode number are required."},
                status=400,
            )

        item = StockItem.objects.filter(id=int_itemid).first()

        if not item:
            return Response({"status": 0, "reason": "Item not found."}, status=404)

        item.barcode = vchr_barcode
        item.save()

        # Generate the barcode as SVG
        code128 = Code128(
            vchr_barcode, writer=CustomSVGWriter(module_height=15, module_width=5.0)
        )
        buffer = BytesIO()
        code128.write(buffer)
        buffer.seek(0)

        # Convert SVG to PNG
        svg_data = buffer.getvalue()
        png_output = BytesIO()
        cairosvg.svg2png(
            bytestring=svg_data,
            write_to=png_output,
            output_height=2000,
            output_width=1600,
        )
        png_output.seek(0)

        # Encode PNG to base64
        barcode_image_base64 = base64.b64encode(png_output.getvalue()).decode("utf-8")

        dct_data = {
            "barcode_image": f"data:image/png;base64,{barcode_image_base64}",
            "item_id": item.id,
            "item_name": item.name if item_name_flag else "",
            "selling_price": item.selling_price if selling_price else "",
            "company_name": item.organization_id if company_name else "",
            "item_code": item.item_code,
        }

        html_output = barcode_print(dct_data)

        # Save PDF
        file_path = os.path.join(settings.MEDIA_ROOT, "barcodes")
        os.makedirs(file_path, exist_ok=True)
        str_file_name = (
            f"Barcode_Generation-{datetime.now().strftime('%d_%m_%Y_%H_%M_%S_%f')}.pdf"
        )
        pdf_file_path = os.path.join(file_path, str_file_name)

        options = {
            "page-width": "50mm",
            "page-height": "40mm",
            "dpi": 300,
            "disable-smart-shrinking": "",
            "enable-local-file-access": "",
        }

        pdfkit.from_string(html_output, pdf_file_path, options=options)

        # Encode PDF to base64
        with open(pdf_file_path, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read()).decode("utf-8")

        str_request_protocol = "https" if request.is_secure() else "http"

        return Response(
            {
                "status": 1,
                "file_url": f"{str_request_protocol}://{request.META['HTTP_HOST']}/media/barcodes/{str_file_name}",
                "dct_data": dct_data,
                "encoded_pdf": encoded_string,
            }
        )

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"Error in barcode_print_view: {e} at line {exc_tb.tb_lineno}")
        return Response(
            {"status": 0, "reason": "An error occurred. Please try again later."},
            status=500,
        )
