
import urllib.request
import urllib.parse
# from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from threading import Thread
import requests

from django.utils.crypto import get_random_string


# from django.utils.timezone import datetime


# from order.models import Order, OrderItem
from datetime import timedelta
import datetime

from django.db.models import Case, Value, When
# from notification.models import FCMDevice
from django.contrib.contenttypes.models import ContentType


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        # print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# def generate_unique_id(size=8, chars=string.ascii_lowercase + string.digits):
#     return ''.join(random.choice(chars) for _ in range(size))


# def generate_form_errors(args,formset=False):
#     message = ''
#     if not formset:
#         for field in args:
#             if field.errors:
#                 message += field.errors  + "|"
#         for err in args.non_field_errors():
#             message += str(err) + "|"

#     elif formset:
#         for form in args:
#             for field in form:
#                 if field.errors:
#                     message +=field.errors + "|"
#             for err in form.non_field_errors():
#                 message += str(err) + "|"
#     return message[:-1]

def get_auto_id(model):
    queryset = model.objects.all()
    if queryset.exists():
        return int(queryset.order_by("-auto_id","-date_added").first().auto_id) + 1
    else:
        return 1

# def get_auto_id(model):
#     """Generate a unique auto_id for the given model_class."""
#     last_instance = model.objects.last()
#     if last_instance:
#         return last_instance.auto_id + 1
#     else:
#         return 1 
# def get_voucher_number(institute):
#     voucher_number = 1
#     latest_voucher_numbers =  InstituteLedgerItem.objects.filter(institute_ledger__institute=institute.id,transaction_type="debit").order_by("-auto_id")[:1]
#     if latest_voucher_numbers:
#         for item in latest_voucher_numbers:
#             print("latest_voucher_number",item.voucher_number)
#             print("type",type(item))
#             if item.voucher_number is not None :
#                 voucher_number = item.voucher_number + 1
#     return voucher_number


# def get_receipt_number(institute):
#     receipt_number = 1
#     latest_receipt_numbers =  InstituteLedgerItem.objects.filter(institute_ledger__institute=institute.id,transaction_type="credit").order_by("-auto_id")[:1]
#     if latest_receipt_numbers:
#         for item in latest_receipt_numbers:
#             print("latest_receipt_number",item.receipt_number)
#             print("type",type(item))
#             if item.receipt_number is not None :
#                 receipt_number = item.receipt_number + 1
#     return receipt_number
        



# def financial_year_create_or_exists(institute,request,recieved_starting_date=None,recievd_closing_date=None,date=None):
#     finanacial_year_list = InstituteFinancialYear.objects.filter(institute=institute,starting_date=recieved_starting_date,closing_date=recievd_closing_date,is_deleted=False) or \
#             (InstituteFinancialYear.objects.filter(institute=institute,starting_date__gte=date,closing_date__lte=date,is_deleted=False))
        

#     if finanacial_year_list.exists():
#         return finanacial_year_list.last()
#     else :
#         if recieved_starting_date and recievd_closing_date :
#             finanacial_year = InstituteFinancialYear.objects.create(
#             auto_id = get_auto_id(InstituteFinancialYear),
#             creator = request.user,
#             institute = institute,
#             starting_date = recieved_starting_date,
#             closing_date = recievd_closing_date,
#             opening_balance = 0,
#             total_income=0,
#             total_expense=0,
#             balance=0
#             )

#     return finanacial_year



# def financial_year_openig_balance_update_for_ledgers(institute_ledger,is_delete,request):
#     mahall= Institute.objects.get(id =institute_ledger.institute.id,is_deleted=False).mahall
#     mahall_financial_year_starting_month = Mahall.objects.get(id= mahall.id,is_deleted=False).financial_year_starting_month

#     today = datetime.date.today()
#     if today.month<mahall_financial_year_starting_month:
#         year=today.year-1
#     else :
#         year=today.year
#     recieved_starting_date = datetime.date(year, mahall_financial_year_starting_month, 1)
#     recievd_closing_date = datetime.date(year + 1 , mahall_financial_year_starting_month, 1) - timedelta(days=1)

#     finanacial_year = financial_year_create_or_exists(institute_ledger.institute,request,recieved_starting_date,\
#         recievd_closing_date,institute_ledger.date_added)

#     if(is_delete):
#         institute_ledger.opening_balance = -1 * institute_ledger.opening_balance
#     finanacial_year.opening_balance += institute_ledger.opening_balance
#     finanacial_year.balance += institute_ledger.opening_balance
#     finanacial_year.save()

#     if(InstituteWallet.objects.filter(institute=institute_ledger.institute,is_bank=False).exists()):
#         institute_wallet = InstituteWallet.objects.filter(institute=institute_ledger.institute,is_bank=False).first() 
#         institute_wallet.balance += institute_ledger.opening_balance
#         institute_wallet.save()
#     else:
#         institute_wallet = InstituteWallet.objects.create(
#             institute=institute_ledger.institute,
#             balance = institute_ledger.opening_balance,
#             description = "",
#             institute_wallet_name = "Cash in hand",
#             auto_id =  get_auto_id(InstituteWallet)
#         ) 

#     return True

# def financial_year_income_expense_balance_update_for_ledger_items(institute_ledger_item,is_delete,request):
#     try:
#         ledger_item_date = institute_ledger_item.date
#         institute_ledger = InstituteLedger.objects.get(id =institute_ledger_item.institute_ledger.id,is_deleted=False)
#         institute = institute_ledger.institute
#         mahall= Institute.objects.get(id = institute.id,is_deleted=False).mahall
#         mahall_financial_year_starting_month = Mahall.objects.get(id= mahall.id,is_deleted=False).financial_year_starting_month

#         if ledger_item_date.month<mahall_financial_year_starting_month:
#             year=ledger_item_date.year-1
#         else :
#             year=ledger_item_date.year
#         recieved_starting_date = datetime.date(year, mahall_financial_year_starting_month, 1)
#         recievd_closing_date = datetime.date(year + 1 , mahall_financial_year_starting_month, 1) - timedelta(days=1)

#         finanacial_year = financial_year_create_or_exists(institute,request,recieved_starting_date,recievd_closing_date,ledger_item_date)
#         if(is_delete):
#             institute_ledger_item.amount= -1 * institute_ledger_item.amount
#         if institute_ledger_item.transaction_type == "credit":
#             balance = float(finanacial_year.balance)
#             finanacial_year.balance = balance + float(institute_ledger_item.amount)
#             total_income = float(finanacial_year.total_income)
#             finanacial_year.total_income = total_income+ float(institute_ledger_item.amount)

#         elif institute_ledger_item.transaction_type == "debit" :
#             balance = float(finanacial_year.balance)
#             finanacial_year.balance = balance - float(institute_ledger_item.amount)
#             total_expense = float(finanacial_year.total_expense)
#             finanacial_year.total_expense = total_expense + float(institute_ledger_item.amount)

#         else :
#             data = {"Access Denied !"}
#         finanacial_year.save()
#         return True
#     except:
#         return False
    




# def committee_meeting_attendance_percentage(committee_meeting_attendance,request):
#     committee = CommitteeMeeting.objects.get(id=committee_meeting_attendance.committee_meeting.id,is_deleted=False).committee
#     total_members_coutn = CommitteeMember.objects.filter(committee=committee,is_deleted=False).count()
#     attandance_count = CommitteeMeetingAttendance.objects.filter(committee_meeting=committee_meeting_attendance.committee_meeting,is_deleted=False).count()
#     attadance_percentage = int((attandance_count/total_members_coutn)*100)
#     CommitteeMeeting.objects.filter(id=committee_meeting_attendance.committee_meeting.id,is_deleted=False).update(attandance_percentage=attadance_percentage)
#     return True




# def get_auto_id(model):
#     year = str(datetime.now().date().year)
#     auto_id = "1-" + year
#     if(model.objects.all().exists()):
#         latest_auto_id = model.objects.all().order_by("-date_added").first()
#         arr = str(latest_auto_id.auto_id).split("-")
#         if(arr[1]==year):
#             latest_date = latest_auto_id.date_added
#             instances = model.objects.filter(date_added = latest_date)
#             count = 0
#             for item in instances:
#                 arr = str(latest_auto_id.auto_id).split("-")
#                 if(int(arr[0])>count):
#                     count = arr[0]
#             x = int(count) + 1
#             auto_id =  str(x) + "-" + year  
#     return auto_id


# def get_ref_id(model):
#     ref_id = 1
#     latest_ref_id = model.objects.all().order_by("-ref_id")[:1]
    
#     if latest_ref_id:
#         for ref in latest_ref_id:
#             ref_id = ref.ref_id + 1       
#     return ref_id


# def get_pk_id(model):
#     pk_id = 1
#     latest_pk_id =  model.objects.all().order_by("-date_joined")[:1]
#     if latest_pk_id:
#         for auto in latest_pk_id:
#             pk_id = auto.pk + 1
#     return pk_id



# def get_timezone(request):
#     if "set_user_timezone" in request.session:
#         user_time_zone = request.session['set_user_timezone']
#     else:
#         user_time_zone = "Asia/Kolkata"
#     return user_time_zone
 
# def sendSMS(phone, message,):
    # data =  urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
    #     'message' : message, 'sender': sender,})
    # data = data.encode('utf-8')
    # request = urllib.request.Request("https://api.textlocal.in/send/?")
    # f = urllib.request.urlopen(request, data)
    # fr = f.read()

    # print(message)
    # return(True)


# def send_common_mail(html_context,to_email,subject,template):
#     def func(html_context,to_email,subject,template):
#         html_content = render_to_string(template, html_context)
#         r = requests.post('https://mail-sender.vingb.com/custom-mail/c405249d-eb67-43d4-ba0c-c1c24840eeba', data={
#             "to_email": to_email,
#             "subject": subject,
#             "html_data": html_content
#         })
    
#     t1 = ThreadWithReturnValue(target=func,args=(html_context,to_email,subject,template))
#     t1.start()



# 28/10/2022
def sendSMS(numbers, message,):
    r="sent sms"
    # r = requests.post('https://mail-sender.vingb.com/send_sms_view/5a187066-5773-49a7-9edd-474d8754665b/9202afdb-ef44-4c6b-ad1f-667c09ea6d85/', data={
    #         "phone":numbers,
    #         "message":message,
    #         "sender":"SAMAS"
    #     })
    return(r)

# def sendSMS(apikey, numbers, sender, message,):
#     data =  urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
#         'message' : message, 'sender': sender,})
#     data = data.encode('utf-8')
#     request = urllib.request.Request("https://api.textlocal.in/send/?")
#     f = urllib.request.urlopen(request, data)
#     fr = f.read()
#     return(fr)





# def send_notification(user_id, title, message, data):
#     try:
#         device = FCMDevice.objects.filter(user=user_id).last()
#         result = device.send_message(title=title, body=message, data=data, 
#            sound=True)
#         return result
#     except:
#         pass







# def send_common_mail(html_context,text_content,from_email,to_email,subject):

#     def func(html_context,text_content,from_email,to_email,subject):
#         html_content = render_to_string('email_templates/common_template1.html', html_context)
#         msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()


#     t1 = ThreadWithReturnValue(target=func,args=(html_context,text_content,from_email,to_email,subject,))
#     t1.start()


    # func(html_context,text_content,from_email,to_email,subject)

# def password_generater(length):
#     length = 8
#     chars = string.ascii_letters + string.digits + '!@#$%^&*()'
#     rnd = random.SystemRandom()
#     return(''.join(rnd.choice(chars) for i in range(length)))


# def mahall_institute_and_ledgers():
#         mahalls = Mahall.objects.filter(is_deleted=False)
#         Institute.objects.all().delete()
#         for mahall in mahalls :
#             creator = mahall.creator

#             if not Institute.objects.filter(mahall=mahall,institute_type = "mahall",is_deleted=False).exists():
#                 institute = Institute.objects.create(
#                     auto_id = get_auto_id(Institute),
#                     creator = creator,
#                     mahall = mahall,
#                     institute_english_name =mahall.mahall_english_name,
#                     institute_malayalam_name =mahall.mahall_malayalam_name,
#                     institute_place = mahall.place,
#                     logo = mahall.logo,
#                     established_date= mahall.established_date,
#                     institute_type = "mahall"
#                     )
#             institute=Institute.objects.get(mahall=mahall,institute_type ="mahall",is_deleted=False)
#             if not InstituteLedger.objects.filter(institute=institute,institute_ledger_name="main",is_deleted=False).exists():
#                 InstituteLedger.objects.create(
#                         auto_id = get_auto_id(InstituteLedger),
#                         creator = creator,
#                         institute = institute,
#                         institute_ledger_name= "main",
#                         balance=0,
#                         description = institute.institute_english_name,
#                         )
#             if not InstituteLedger.objects.filter(institute=institute, institute_ledger_name="varisankya",is_deleted=False).exists():
#                 InstituteLedger.objects.create(
#                         auto_id = get_auto_id(InstituteLedger),
#                         creator = creator,
#                         institute = institute,
#                         institute_ledger_name="varisankya",
#                         balance=0,
#                         description = "Mahall Varisankya",
#                         )




# def mahall_referral_code_generation():
#         mahalls = Mahall.objects.filter(is_deleted=False)
#         for mahall in mahalls :
#             print("///////////////")
#             referral_code = mahall.custom_id+get_random_string(4)
#             mahall.referral_code=referral_code
#             mahall.save()


# def toBool(val):
#     if(val==True or val == "True" or val== 'true'):
#         return True
#     else:
#         return False
    
# def custom_id_sort(queryset,is_reverse=False):
#     def is_digit(x):
#         mahall_custom_id = str(x.mahall_custom_id).upper() 
#         try:
#             return int("".join([i for i in mahall_custom_id if i.isdigit()]))
#         except:
#             return 0

#     def is_not_digit(x):
#         mahall_custom_id = str(x.mahall_custom_id).upper() 
#         return str("".join([i for i in mahall_custom_id if (not i.isdigit())]))
#     try:
#         dup_queryset = sorted(queryset, key=is_not_digit,reverse=is_reverse)
#         dup_queryset = sorted(dup_queryset, key=is_digit,reverse=is_reverse)
#         preserved = Case(*[When(pk=item.pk, then=pos) for pos, item in enumerate(dup_queryset)])
#         queryset = queryset.order_by(preserved)
#     except:
#         pass    

    # for item in dup_queryset:
    #     print(item.mahall_custom_id)

    

    # return queryset


# def get_content_type_for_model(obj):

#     return ContentType.objects.get_for_model(obj, for_concrete_model=False)



# def IsAdmin(self,group_name):
#     user = self.request.user
#     return (self.request.headers["Role"]=="admin") and (user.groups.filter(name=group_name).exists())

# def IsMahallUser(self,permission):
#     user = self.request.user
#     if(permission =='perm_view'):
#         return (self.request.headers["Role"]=="mahall_user") and (MahallUser.objects.filter(account=user,is_deleted=False,perm_view=True).exists())
#     elif(permission =='perm_create'):
#         return (self.request.headers["Role"]=="mahall_user") and (MahallUser.objects.filter(account=user,is_deleted=False,perm_create=True).exists())
#     elif(permission =='perm_update'):
#         return (self.request.headers["Role"]=="mahall_user") and (MahallUser.objects.filter(account=user,is_deleted=False,perm_update=True).exists())
#     elif(permission =='perm_delete'):
#         return (self.request.headers["Role"]=="mahall_user") and (MahallUser.objects.filter(account=user,is_deleted=False,perm_delete=True).exists())
#     else:
#         return False
    
# def IsInstituteUser(self,permission):
#     user = self.request.user
#     if(permission =='perm_view'):
#         return (self.request.headers["Role"]=="institute_user") and (InstituteUser.objects.filter(account=user,is_deleted=False,perm_view=True).exists())
#     elif(permission =='perm_create'):
#         return (self.request.headers["Role"]=="institute_user") and (InstituteUser.objects.filter(account=user,is_deleted=False,perm_create=True).exists())
#     elif(permission =='perm_update'):
#         return (self.request.headers["Role"]=="institute_user") and (InstituteUser.objects.filter(account=user,is_deleted=False,perm_update=True).exists())
#     elif(permission =='perm_delete'):
#         return (self.request.headers["Role"]=="institute_user") and (InstituteUser.objects.filter(account=user,is_deleted=False,perm_delete=True).exists())
#     else:
#         return False