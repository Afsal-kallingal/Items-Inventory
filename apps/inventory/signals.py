# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from apps.inventory.models import InventoryTransaction, StockReport
# from django.db import transaction
# import logging

# logger = logging.getLogger(__name__)

# @receiver(post_save, sender=InventoryTransaction)
# def update_stock_report_on_save(sender, instance, created, **kwargs):
#     """
#     Signal to update StockReport whenever an InventoryTransaction is saved.
#     """
#     try:
#         # Ensure stock report exists or create it
#         stock_report, created_report = StockReport.objects.get_or_create(
#             organization_id=instance.organization_id,
#             item=instance.item,
#             godown=instance.godown,
#             defaults={"opening_balance": 0, "closing_balance": 0},
#         )

#         # Handle new transactions
#         if created:
#             if instance.transaction_type == "Inbound":
#                 stock_report.closing_balance += instance.quantity
#             elif instance.transaction_type == "Outbound":
#                 stock_report.closing_balance -= instance.quantity

#         # Handle updates to existing transactions
#         else:
#             # Fetch the previous transaction state
#             try:
#                 previous_transaction = InventoryTransaction.objects.get(pk=instance.pk)
#                 if previous_transaction.transaction_type == "Inbound":
#                     stock_report.closing_balance -= previous_transaction.quantity
#                 elif previous_transaction.transaction_type == "Outbound":
#                     stock_report.closing_balance += previous_transaction.quantity

#                 # Apply the current transaction state
#                 if instance.transaction_type == "Inbound":
#                     stock_report.closing_balance += instance.quantity
#                 elif instance.transaction_type == "Outbound":
#                     stock_report.closing_balance -= instance.quantity
#             except InventoryTransaction.DoesNotExist:
#                 logger.warning("Previous transaction state could not be retrieved.")

#         # Save updated stock report
#         stock_report.save()

#     except Exception as e:
#         logger.error(f"Error in update_stock_report_on_save: {e}")


# @receiver(post_delete, sender=InventoryTransaction)
# def update_stock_report_on_delete(sender, instance, **kwargs):
#     """
#     Signal to update StockReport whenever an InventoryTransaction is deleted.
#     """
#     try:
#         # Retrieve stock report
#         stock_report = StockReport.objects.get(
#             organization_id=instance.organization_id,
#             item=instance.item,
#             godown=instance.godown,
#         )

#         # Revert the transaction's effect
#         if instance.transaction_type == "Inbound":
#             stock_report.closing_balance -= instance.quantity
#         elif instance.transaction_type == "Outbound":
#             stock_report.closing_balance += instance.quantity

#         # Save updated stock report
#         stock_report.save()

#     except StockReport.DoesNotExist:
#         logger.warning(f"StockReport not found for {instance.organization_id}, {instance.item}, {instance.godown}.")
#     except Exception as e:
#         logger.error(f"Error in update_stock_report_on_delete: {e}")
