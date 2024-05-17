import email
import json
from django.forms import PasswordInput
import requests
from home import *;
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from .models import User
from django.contrib.auth import authenticate, login,logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from patient.models import Patient
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import User
from django.contrib.auth import authenticate, login,logout
from django.utils.encoding import DjangoUnicodeDecodeError
from . import forms,models
from . import models as CMODEL
from .models import *
from .models import PolicyRecord
from . import forms as CFORM
from django.views.generic import View
from .utils import *
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
#for activating user account
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from home.models import Customer, Policy, PolicyRecord, Category, Question
#email
from django.conf import settings
from django.core.mail import EmailMessage
#threading
import threading
#reset passwor generater
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from .models import Customer
from django.contrib.auth.hashers import make_password
from django.conf import settings

class EmailThread(threading.Thread):
       def __init__(self, email_message):
              super().__init__()
              self.email_message=email_message
       def run(self):
              self.email_message.send()
# Create your views here.


# @never_cache
# @login_required(login_url='/handlelogin/')
def index(request):
    return render(request, 'index.html')
    #return HttpResponse("Hello World..!")
User = get_user_model()

def Sign_up(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.warning(request, "Password is not matching")
            return render(request, 'signup.html')

        try:
            # Check if the email is already taken
            if User.objects.get(username=email):
                messages.warning(request, "Email is already taken")
                return render(request, 'signup.html')
        except User.DoesNotExist:
            pass

        # Create a user with email and password
        user = User.objects.create_user(email=email, password=password, username=email, role='CUSTOMER')
        user.is_active = False
        user.save()

        # Create a Customer instance with additional details
        customer = Customer.objects.create(
            user=user,
            first_name=request.POST['fname'],
            last_name=request.POST['lname'],
            phone=request.POST['phone'],
            aadhaar=request.POST['aadhaar_number'],
            address=request.POST['address'],
            place=request.POST['place'],

            # Add other fields as needed
        )
        
        # Handle image field separately if it's included in the form
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            try:
                # Validate the image file extension
                validate_image_file_extension(profile_picture)
            except ValidationError as e:
                messages.warning(request, f"Invalid image file: {e}")
                return render(request, 'signup.html')

            customer.image = profile_picture

        # # Handle image field separately if it's included in the form
        # if 'image' in request.FILES:
        #     customer.image = request.FILES['image']

        customer.save()

        # Send activation email
        current_site = get_current_site(request)
        email_subject = "Activate your account"
        message = render_to_string('activate.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })

        email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
        email_message.send()

        messages.info(request, "Activate your account by clicking the link sent to your email")
        return redirect('/handlelogin')

    return render(request, 'signup.html')

class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account activated sucessfully")
            return redirect('/handlelogin')
        user.is_active=True
        user.save()
        return redirect('/handlelogin')
        #return render(request,"activatefail.html")

def handlelogin(request):
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['password']
        myuser = authenticate(request, username=username, password=password)
        print(myuser)
        if myuser is not None:
            login(request, myuser)
            request.session['username'] = username

            if myuser.role == 'CUSTOMER':
                #return redirect('customer_dashboard_view')
                return redirect('customer_dashboard')
            elif myuser.role == 'SELLER':
                return HttpResponse("seller login")
            elif myuser.role == 'ADMIN':
                return redirect('/admin_dashboard/')  # Redirect to the admin dashboard page
            elif myuser.role == 'HOSPITAL':
                return redirect('/hospital_dashboard/')
            elif myuser.role == 'STAFF':
                return redirect('staffhome')
            elif myuser.role == 'AGENT':
                return redirect('agenthome')


        else:
            messages.error(request, "Enter valid credentials")
            return redirect('/handlelogin')
    
    response = render(request, 'login.html')
    response['Cache-Control'] = 'no-store, must-revalidate'
    return response

@never_cache
@login_required(login_url='/handlelogin/')
def customer_home(request):
       if 'username' in request.session:
        response = render(request,'customer_page.html')
        response['Cache-Control'] = 'no-store,must-revalidate'
        return response
       else:
             return redirect('handlelogin')

def handlelogout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('/')




@never_cache
@login_required(login_url='/handlelogin/')
def admin_dashboard_view(request):
    dict={
        'total_user':Customer.objects.all().count(),
        'total_policy':Policy.objects.all().count(),
        'total_category':Category.objects.all().count(),
        'total_question':Question.objects.all().count(),
        'total_policy_holder':PolicyRecord.objects.all().count(),
        'approved_policy_holder':PolicyRecord.objects.all().filter(status='Approved').count(),
        'disapproved_policy_holder':PolicyRecord.objects.all().filter(status='Disapproved').count(),
        'waiting_policy_holder':PolicyRecord.objects.all().filter(status='Pending').count(),
    }
    return render(request,'dashboard.html',context=dict)

#################################################################################################
#################################################################################################
#################################################################################################

#@login_required(login_url='adminlogin')
def admin_view_customer_view(request):
    # Fetch data from the User and Customer models
    all_customers = Customer.objects.all()
    #all_users = User.objects.all()


    return render(request, 'admin/admin_view_customer.html', {'all_customers': all_customers})


@never_cache
@login_required(login_url='adminlogin')

def update_customer_view(request,pk):
    customer=CMODEL.Customer.objects.get(id=pk)
    user=CMODEL.User.objects.get(id=customer.user_id)
    userForm=CFORM.CustomerUserForm(instance=user)
    customerForm=CFORM.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=CFORM.CustomerUserForm(request.POST,instance=user)
        customerForm=CFORM.CustomerForm(request.POST,request.FILES,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('admin-view-customer')
    return render(request,'admin/update_customer.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=CMODEL.Customer.objects.get(id=pk)
    user=User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return HttpResponseRedirect('/admin-view-customer')



def admin_category_view(request):
    return render(request,'admin/admin_category.html')

def admin_add_category_view(request):
    categoryForm=forms.CategoryForm() 
    if request.method=='POST':
        categoryForm=forms.CategoryForm(request.POST)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('admin-view-category')
    return render(request,'admin/admin_add_category.html',{'categoryForm':categoryForm})

def admin_view_category_view(request):
    categories = Category.objects.all()
    return render(request,'admin/admin_view_category.html',{'categories':categories})

def admin_delete_category_view(request):
    categories = Category.objects.all()
    return render(request,'admin/admin_delete_category.html',{'categories':categories})
    
def delete_category_view(request,pk):
    category = Category.objects.get(id=pk)
    category.delete()
    return redirect('admin-delete-category')

def admin_update_category_view(request):
    categories = Category.objects.all()
    return render(request,'admin/admin_update_category.html',{'categories':categories})

@login_required(login_url='adminlogin')
def update_category_view(request,pk):
    category = Category.objects.get(id=pk)
    categoryForm=forms.CategoryForm(instance=category)
    
    if request.method=='POST':
        categoryForm=forms.CategoryForm(request.POST,instance=category)
        
        if categoryForm.is_valid():

            categoryForm.save()
            return redirect('admin-update-category')
    return render(request,'admin/update_category.html',{'categoryForm':categoryForm})
  
def admin_policy_view(request):
    return render(request,'admin/admin_policy.html')


def admin_add_policy_view(request):
    policyForm=forms.PolicyForm() 
    
    if request.method=='POST':
        policyForm=forms.PolicyForm(request.POST)
        if policyForm.is_valid():
            categoryid = request.POST.get('category')
            category = Category.objects.get(id=categoryid)
            
            policy = policyForm.save(commit=False)
            policy.category=category
            policy.save()
            return redirect('admin-view-policy')
    return render(request,'admin/admin_add_policy.html',{'policyForm':policyForm})

def admin_view_policy_view(request):
    policies = Policy.objects.all()
    return render(request,'admin/admin_view_policy.html',{'policies':policies})

def admin_update_policy_view(request):
    policies = Policy.objects.all()
    return render(request,'admin/admin_update_policy.html',{'policies':policies})

@login_required(login_url='adminlogin')
def update_policy_view(request,pk):
    policy = Policy.objects.get(id=pk)
    policyForm=forms.PolicyForm(instance=policy)
    
    if request.method=='POST':
        policyForm=forms.PolicyForm(request.POST,instance=policy)
        
        if policyForm.is_valid():

            categoryid = request.POST.get('category')
            category = Category.objects.get(id=categoryid)
            
            policy = policyForm.save(commit=False)
            policy.category=category
            policy.save()
           
            return redirect('admin-update-policy')
    return render(request,'admin/update_policy.html',{'policyForm':policyForm})
  
  
def admin_delete_policy_view(request):
    policies = Policy.objects.all()
    return render(request,'admin/admin_delete_policy.html',{'policies':policies})
    
def delete_policy_view(request,pk):
    policy = Policy.objects.get(id=pk)
    policy.delete()
    return redirect('admin-delete-policy')

###

def admin_view_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.all()
    return render(request,'admin/admin_view_policy_holder.html',{'policyrecords':policyrecords})

def admin_view_approved_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.all().filter(status='Approved')
    return render(request,'admin/admin_view_approved_policy_holder.html',{'policyrecords':policyrecords})

def admin_view_disapproved_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.all().filter(status='Disapproved')
    return render(request,'admin/admin_view_disapproved_policy_holder.html',{'policyrecords':policyrecords})

def admin_view_waiting_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.all().filter(status='Pending')
    return render(request,'admin/admin_view_waiting_policy_holder.html',{'policyrecords':policyrecords})

def approve_request_view(request,pk):
    policyrecords = PolicyRecord.objects.get(id=pk)
    policyrecords.status='Approved'
    policyrecords.save()
    return redirect('admin-view-policy-holder')

def disapprove_request_view(request,pk):
    policyrecords = PolicyRecord.objects.get(id=pk)
    policyrecords.status='Disapproved'
    policyrecords.save()
    return redirect('admin-view-policy-holder')


def admin_question_view(request):
    questions = Question.objects.all()
    return render(request,'admin/admin_question.html',{'questions':questions})

def update_question_view(request,pk):
    question = Question.objects.get(id=pk)
    questionForm=forms.QuestionForm(instance=question)
    
    if request.method=='POST':
        questionForm=forms.QuestionForm(request.POST,instance=question)
        
        if questionForm.is_valid():

            admin_comment = request.POST.get('admin_comment')
            
            
            question = questionForm.save(commit=False)
            question.admin_comment=admin_comment
            question.save()
           
            return redirect('admin-question')
    return render(request,'admin/update_question.html',{'questionForm':questionForm})

##################################################################################################
##################################################################################################
##################################################################################################


@never_cache
@login_required(login_url='/handlelogin/')
def hospital_dashboard(request):
      patients=Patient.objects.all()

      return render(request,"hospital/hospital_dashboard.html",{'patients': patients})


@login_required(login_url='/handlelogin/')
@never_cache
@login_required(login_url='/handlelogin/')
def customer_dashboard(request):
    customer = get_object_or_404(Customer, user=request.user)
    

    available_policy_count = Policy.objects.all().count()
    applied_policy_count = PolicyRecord.objects.filter(customer=customer).count()
    total_category_count = Category.objects.all().count()
    total_question_count = Question.objects.filter(customer=customer).count()

    context = {
        'customer': customer,
        'available_policy': available_policy_count,
        'applied_policy': applied_policy_count,
        'total_category': total_category_count,
        'total_question': total_question_count,
    }

    return render(request, 'customer/customer_dashboard.html', context)

# def apply_policy_view(request):
#     customer = get_object_or_404(models.Customer,user_id=request.user.id)
#     policies = CMODEL.Policy.objects.all()
#     return render(request,'customer/apply_policy.html',{'policies':policies,'customer':customer})

from django.shortcuts import render, get_object_or_404
import razorpay
from . import models as CMODEL  # Assuming your models are in models.py within the same app

# Initialize Razorpay client

def apply_policy_view(request):
    customer = get_object_or_404(CMODEL.Customer, user_id=request.user.id)
    policies = CMODEL.Policy.objects.all()

    # Fixed amount for Razorpay payment, for demonstration
    

    # Context for rendering in the template
    context = {
        
        'policies': policies,
        'customer': customer
    }

    # Use the 'apply_policy.html' template or another template that includes the Razorpay JavaScript code
    return render(request, 'customer/apply_policy.html', context=context)

import razorpay
from django.shortcuts import render
from django.conf import settings

razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

# views.py

def payment2(request, item_id):
    
    currency = 'INR'
    amount = 2000 * 100  # Rs. 2000, converted to paise

    # You can use item_id here, for example, to get data related to what is being paid for
    # item = get_object_or_404(MyModel, id=item_id)  # Assuming you're paying for items stored in a model

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='1'))

    razorpay_order_id = razorpay_order['id']
    callback_url = 'your_callback_url_here'  # Specify your callback URL here

    context = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
        'callback_url': callback_url,
        # 'item': item,  # You can pass the item to the template, if necessary
    }
    return render(request, 'customer/payment2.html', context=context)








def apply_view(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = CMODEL.Policy.objects.get(id=pk)
    policyrecord = CMODEL.PolicyRecord()
    policyrecord.Policy = policy
    policyrecord.customer = customer
    policyrecord.save()
    return redirect('history')

def history_view(request):
    customer = Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.PolicyRecord.objects.all().filter(customer=customer)
    return render(request,'customer/history.html',{'policies':policies,'customer':customer})

def ask_question_view(request):
    customer = Customer.objects.get(user_id=request.user.id)
    questionForm=CFORM.QuestionForm() 
    
    if request.method=='POST':
        questionForm=CFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            
            question = questionForm.save(commit=False)
            question.customer=customer
            question.save()
            return redirect('question-history')
    return render(request,'customer/ask_question.html',{'questionForm':questionForm,'customer':customer})

def question_history_view(request):
    customer = Customer.objects.get(user_id=request.user.id)
    questions = CMODEL.Question.objects.all().filter(customer=customer)
    return render(request,'customer/question_history.html',{'questions':questions,'customer':customer})



"""def employee_signup(request):
    if request.method == 'POST':
        # Handle User registration (username and password)
        email = request.POST['email']
        password = request.POST['password']

        # Set the username to the user's email
        username = email

        # Create a User instance
        user = User.objects.create_user(username=username, email=email, password=password)

        # Handle EmployeeRegistration
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        address = request.POST['address']
        resume_upload = request.FILES['resume_upload']

        # Create an EmployeeRegistration instance
        employee_registration = EmployeeRegistration(
            user=user,  # Link the User to the EmployeeRegistration
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            resume_upload=resume_upload
        )
        employee_registration.save()

        # Redirect to a success page or do other necessary actions
        return redirect('index')  # Change 'success_page' to the URL for the success page

    # Handle form errors and render the registration form
    return render(request, 'employee_signup.html')"""

   

# def Sign_up(request):
#     if request.method=="POST":
#             fname=request.POST['fname']
#             lname=request.POST['lname']
#             email=request.POST['email']
#             #phone=request.POST['phone']
#             username=email
            
#             password=request.POST['password']
#             confirm_password=request.POST['confirm_password']


            
#             if password!=confirm_password:
#                     messages.warning(request,"password is not matching")
#                     return render(request,'signup.html')
#             try:
#                       if User.objects.get(username=email):
#                              messages.warning(request,"Email is already taken")
#                              return render(request,'signup.html')
#             except Exception as identifiers:
#                       pass

#             user=User.objects.create_user(first_name=fname,last_name=lname,email=email,password=password,username=username,role='CUSTOMER')
#             user.is_active=False 
#             user.save()
#             current_site=get_current_site(request)  
#             email_subject="Activate your account"
#             message=render_to_string('activate.html',{
#                    'user':user,
#                    'domain':current_site.domain,
#                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
#                    'token':generate_token.make_token(user)


#             })

#             email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
#             EmailThread(email_message).start()
#             messages.info(request,"Active your account by clicking the link send to your email")



           
#             return redirect('/handlelogin')
           
             
           
#     return render(request,'signup.html')


# def customer_dashboard(request):
#     # dict={
#     #     'customer':get_object_or_404(models.Customer,user_id=request.user.id),
#     #     'available_policy':CMODEL.Policy.objects.all().count(),
#     #     'applied_policy':CMODEL.PolicyRecord.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
#     #     'total_category':CMODEL.Category.objects.all().count(),
#     #     'total_question':CMODEL.Question.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),

#     # }
#     return render(request,'customer/customer_dashboard.html')





from .forms import CustomerSelectForm
from .models import *

def select_customer(request):
    if request.method == 'POST':
        form = CustomerSelectForm(request.POST)
        if form.is_valid():
            customer_id = form.cleaned_data['customer'].id
            return redirect('customer_details', customer_id=customer_id)
    else:
        form = CustomerSelectForm()
    return render(request, 'select_customer.html', {'form': form})

def customer_details(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    return render(request, 'customer_details.html', {'customer': customer})

def customer_details(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    plans = VehiclePlan.objects.all()
    return render(request, 'customer_details.html', { 'customer': customer,'plans': plans})

def staff_view_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.all()
    return render(request,'staff/staff-view-policy-holder.html',{'policyrecords':policyrecords})


def staff_view_approved_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.all().filter(status='Approved')
    return render(request,'staff/staff_view_approved_policy_holder.html',{'policyrecords':policyrecords})

def staff_view_disapproved_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.all().filter(status='Disapproved')
    return render(request,'staff/staff_view_disapproved_policy_holder.html',{'policyrecords':policyrecords})

def staff_view_waiting_policy_holder_view(request):
    policyrecords = PolicyRecord.objects.all().filter(status='Pending')
    return render(request,'staff/staff_view_waiting_policy_holder.html',{'policyrecords':policyrecords})

def staff_approve_request_view(request,pk):
    policyrecords = PolicyRecord.objects.get(id=pk)
    policyrecords.status='Approved'
    policyrecords.save()
    return redirect('staff-view-policy-holder')

def staff_disapprove_request_view(request,pk):
    policyrecords = PolicyRecord.objects.get(id=pk)
    policyrecords.status='Disapproved'
    policyrecords.save()
    return redirect('staff-view-policy-holder')



# from django.shortcuts import render, redirect
# from django.utils import timezone
# from .models import Office
# from django.contrib.auth.models import User

# def office_registration(request):
#     if request.method == "POST":
#         # Process form data
#         address = request.POST.get('address')
#         place = request.POST.get('place')
#         location = request.POST.get('location')
#         pin = request.POST.get('pin')
#         phone = request.POST.get('phone')
#         district = request.POST.get('district')
#         state = request.POST.get('state')
#         regdate = timezone.now().date()  # Capture current date for registration
        
#         # Create and save new Office instance
#         office = Office.objects.create(
#             address=address, place=place, location=location,
#             pin=pin, phone=phone, district=district, state=state, regdate=regdate
#         )

#         # Assuming you want to register a user when an office is registered
#         # Note: Make sure the user registration logic is relevant and secure
#         user = User.objects.create_user(username=place, password='default_password', is_active=False)
#         user.save()

#         # Redirect to a success page or back to form with a success message
#         return redirect('admin/admin_office_registration_successfull.html')  # Replace 'success_page_url' with your actual URL
#     else:
#         # GET request, show empty form
#         return render(request, 'admin_office_registration.html')

    

@never_cache
@login_required(login_url='/handlelogin/')
def staff_home(request):
    return render(request,'staff_home.html')

from django.conf import settings

from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from .models import Agent,Staff

@never_cache
def add_agent(request):
    if request.method == 'POST':
        # User model fields
        email = request.POST['email']
        name = request.POST['name']

        # Generate a random password
        password = get_random_string(length=8)

        # Create User instance
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name,role=User.Role.AGENT)
        user.save()

        # Agent model fields
        agent = Agent(
            user=user,
            name=name,
            address=request.POST['address'],
            place=request.POST['place'],
            location=request.POST['location'],
            pin=request.POST['pin'],
            phone=request.POST['phone'],
            gender=request.POST['gender'],
            qualification=request.POST['qualification'],
            aadhar=request.POST['aadhar'],
            registration_date=request.POST['registration_date'],
            # Assuming request.FILES is properly set up in your form for handling file uploads
            photo=request.FILES.get('photo', None)
        )
        agent.save()

        # Send email to the user
        send_mail(
            'Your Account Information',
            f'Your account has been created. Your password is: {password}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return HttpResponse("agent added sucessfully")  # Redirect to a new URL

    return render(request, 'add_agent.html')

def register_staff(request):
    if request.method == "POST":
        # Extracting information from the request
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        place = request.POST['place']
        pin = request.POST['pin']
        district = request.POST['district']
        state = request.POST['state']
        dob = request.POST['dob']
        photo = request.FILES['photo'] if 'photo' in request.FILES else None
        password = request.POST['password']
        
        # Create user instance
        User = get_user_model()
        user = User.objects.create(
            username=email,  # Assuming username is email for simplicity
            email=email,
            password=make_password(password),
            role=User.Role.STAFF
        )
        # Optionally, you can use user.set_password(password) to handle hashing
        user.save()
        
        # Create staff instance
        staff = Staff(
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            place=place,
            pin=pin,
            district=district,
            state=state,
            dob=dob,
            photo=photo
        )
        staff.save()

        # Redirect to a new URL:
        return redirect('staffhome')

    # If a GET (or any other method) we'll create a blank form
    else:
        return render(request, 'register.html')

# Remember to include the appropriate URLconf if you haven't already done so


@never_cache
@login_required(login_url='/handlelogin/')
def agenthome(request):
    return render(request,'agenthome.html')

from .models import Office
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
import datetime

from django.urls import reverse
from django.shortcuts import redirect

@csrf_exempt
def register_office(request):
    if request.method == 'POST':
        new_office = Office(
            address=request.POST.get('address'),
            place=request.POST.get('place'),
            location=request.POST.get('location'),
            pin=request.POST.get('pin'),
            phone=request.POST.get('phone'),
            district=request.POST.get('district'),
            state=request.POST.get('state'),
            regdate=datetime.date.today()
        )
        new_office.save()

        # Redirect to the success page, passing the ID of the newly created office
        return redirect(reverse('office_success', kwargs={'office_id': new_office.officeid}))
    else:
        return render(request, 'admin/admin_office_registration.html')

from django.shortcuts import render, get_object_or_404

def office_detail(request, office_id):
    office = get_object_or_404(Office, officeid=office_id)
    return render(request, 'admin/admin_office_detail.html', {'office': office})


# # Assuming you want a view to display the office details
# def office_detail(request, office_id):
#     office = Office.objects.get(id=office_id)
#     return render(request, 'admin/admin_office_detail.html', {'office': office})

def view_office(request):
    var=Office.objects.all()
    context={
        'var':var
    }
    return render(request, 'admin/admin_office_registration_successfull.html', context)

#staff registration

from django.views.decorators.csrf import csrf_exempt
from .models import Office, Staff
from django.conf import settings

@csrf_exempt
def register_staff(request):
    if request.method == 'POST':
        # Extracting form data using more descriptive names
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        place = request.POST.get('place')
        pin = request.POST.get('pin')
        phone = request.POST.get('phone')
        district = request.POST.get('district')
        state = request.POST.get('state')
        dob = request.POST.get('dob')
        photo = request.FILES.get('file')
        office_id = request.POST.get('office_id')
        designation = request.POST.get('designation')

        # Saving the staff details
        try:
            office = Office.objects.get(pk=office_id)
            staff = Staff(
                office=office,
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                address=office.address,
                place=place,
                pin=pin,
                district=district,
                state=state,
                dob=dob,
                photo=photo
            )
            staff.save()
            return redirect('admin_staff_registration_successful')
        except Exception as e:
            print(e)
            return render(request, 'admin/admin_staff_registration.html', {'error': 'Error while registering the staff'})

    # For GET request, or if there is any other issue
    offices = Office.objects.all()
    return render(request, 'admin/admin_staff_registration.html', {'records': offices})

def list_offices(request):
    offices = Office.objects.all()
    return render(request, 'admin/admin_staff_registration.html', {'records': offices})


def admin_staff_registration_successful(request, staff_id):
    staff = Staff.objects.get(id=staff_id)
    return render(request, 'admin/admin_staff_registration_successfull.html', {'staff': staff})

from django.shortcuts import render, redirect
from .models import VehiclePlan
from django.contrib import messages

def vehicle_plan_registration(request):
    if request.method == 'POST':
        p_type = request.POST.get('t1')
        p_percentage = request.POST.get('t2')
        specifications = request.POST.get('t3')
        depreciation = request.POST.get('t4')

        try:
            # Attempt to convert percentage and depreciation to proper formats
            p_percentage = float(p_percentage)
            depreciation = float(depreciation)

            # Create a new VehiclePlan instance and save it
            new_plan = VehiclePlan(PType=p_type, Ppercentage=p_percentage, sp=specifications, depreciation=depreciation)
            new_plan.save()

            # Show success message
            messages.success(request, 'Vehicle plan registered successfully!')
        except ValueError:
            # Handle error if conversion fails
            messages.error(request, 'Invalid input in numeric fields.')
        except Exception as e:
            # General error handling
            messages.error(request, f'Error registering plan: {str(e)}')

    # Load existing plans to display
    records = VehiclePlan.objects.all()
    return render(request, 'admin/admin_vehicleplan_registration.html', {'records': records})

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import HealthPlan
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Remove this if CSRF token works properly; it's just for demonstration.
def health_plan_registration(request):
    if request.method == 'POST':
        # Extract data from the form
        ptype = request.POST.get('t1')
        ypremium = request.POST.get('t2')
        incper = request.POST.get('t3')
        maxamt = request.POST.get('t4')
        specification = request.POST.get('t5')
        uptoage = request.POST.get('t6')
        
        # Create a new HealthPlan object and save it
        try:
            # hpid = "HP" + str(HealthPlan.objects.count() + 1)  # Simple example to generate a new ID
            health_plan = HealthPlan(
                # hpid=hpid,
                ptype=ptype,
                ypremium=ypremium,
                incper=incper,
                maxamt=maxamt,
                specification=specification,
                uptoage=uptoage
            )
            health_plan.save()
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")

    # Fetch existing plans to display
    records = HealthPlan.objects.all()
    return render(request, 'admin/admin_healthplan_registration.html', {'records': records})


# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from .models import VehiclePolicy, VehiclePlan, Customer
# from decimal import Decimal
# import datetime

# def register_vehicle_policy(request):
#     if request.method == 'POST':
#         try:
#             # Extract and validate data from form
#             vehno = request.POST.get('t2')
#             vehvalue = Decimal(request.POST.get('t3', 0))
#             vpid = request.POST.get('t4')
#             enginno = request.POST.get('t5')
#             chno = request.POST.get('t6')
#             vehcompany = request.POST.get('t8')
#             mfyear = int(request.POST.get('t10', 0))
#             vehphoto = request.FILES.get('file')
#             vehtype = request.POST.get('t11')
#             officeid = request.POST.get('t12')
#             custid = request.POST.get('t1')

#             # Retrieve related objects
#             plan = VehiclePlan.objects.get(id=vpid)
#             customer = Customer.objects.get(id=custid)

#             # Calculate policy amount
#             depreciation_factor = Decimal(plan.depreciation / 100)
#             plan_percentage = Decimal(plan.Ppercentage / 100)
#             policy_amount = (vehvalue - (vehvalue * depreciation_factor)) * (1 + plan_percentage)

#             # Create and save the VehiclePolicy object
#             policy = VehiclePolicy(
#                 custid=customer,
#                 vehno=vehno,
#                 vehvalue=vehvalue,
#                 vpid=plan,
#                 enginno=enginno,
#                 chno=chno,
#                 vehcompany=vehcompany,
#                 mfyear=mfyear,
#                 officeid=officeid,
#                 vehphoto=vehphoto,
#                 vehtype=vehtype,
#                 policyamount=policy_amount,
#                 policydate=datetime.date.today(),
#                 penddate=datetime.date.today() + datetime.timedelta(days=365)  # assuming policy is valid for one year
#             )
#             policy.save()

#             return redirect('policy_success')  # Redirect to a success URL
#         except (VehiclePlan.DoesNotExist, Customer.DoesNotExist, KeyError, ValueError) as e:
#             return HttpResponse(f"Error processing your request: {e}", status=400)
#     else:
#         plans = VehiclePlan.objects.all()
#         offices = Office.objects.all()
#         # customers = Customer.objects.filter(request.user)

#         context = {
#             'plans': plans,
#             'offices': offices,
            
#         }
#         return render(request, 'customer/customer_vehicle_policyissue.html',context)

# def policy_success(request):
#     return render(request, 'customer/customer_vehicle_policyissue_successful.html')


#admin adds Blog

from .forms import BlogPostForm
def add_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.seller = request.user
            blog_post.save()
            return redirect('/add')  # Redirect to the blog post list page
    else:
        form = BlogPostForm()

    return render(request, 'admin/add_blog_post.html', {'form': form})


#Customer views blog
from .models import BlogPost

@never_cache
@login_required(login_url="/auth_app/handlelogin/")
def blog_post_list(request):
    blog_posts = BlogPost.objects.all()
    top_three_posts = BlogPost.objects.order_by('-views')[:3]
    return render(request, 'customer/blog_post_list.html', {'blog_posts': blog_posts,'top_three_posts':top_three_posts})



# Guest user searches agents on map

from django.shortcuts import render
import requests
from .models import Agent

def view_agents(request):
    agents = Agent.objects.all()

    for agent in agents:
        # We will use OpenCage API for a detailed example
        # Make sure to replace 'YOUR_OPENCAGE_API_KEY' with your actual API key
        address = agent.place  # Assuming 'place' has enough address detail for geocoding
        url = f'https://api.opencagedata.com/geocode/v1/json?q={address}&key=YOUR_OPENCAGE_API_KEY'

        response = requests.get(url)
        data = response.json()

        if data.get('results') and data['results'][0].get('geometry'):
            agent.latitude = data['results'][0]['geometry']['lat']
            agent.longitude = data['results'][0]['geometry']['lng']
        else:
            agent.latitude = None
            agent.longitude = None

    return render(request, 'guest_map_agents.html', {'agents': agents})

# Machine learning model(Ensemble learning- Random Forest) for health insurance prediction

import joblib

model = joblib.load('static/random_forest_regressor')
from datetime import datetime
def healthinsurance_prediction(request):
    if request.method == "POST":
        # Extract form data
        dob = datetime.strptime(request.POST['dob'], '%Y-%m-%d').date()
        age = calculate_age(dob)
        weight = float(request.POST['weight'])
        height = float(request.POST['height'])
        children = int(request.POST['children'])
        smoker_str = request.POST['smoker'].lower()  # Convert to lowercase for case-insensitive comparison
        if smoker_str == 'true':
            smoker = True
        elif smoker_str == 'false':
            smoker = False
        region = request.POST['region']

        # Calculate BMI
        bmi = calculate_bmi(weight, height)

        print(age, bmi, children, smoker, region)

        # Perform prediction
        pred = model.predict([[age, bmi, children, smoker, region]])
        print(pred)

        output = {"output": pred}

        return render(request, 'healthinsurance_prediction.html', {'pred': pred})

    return render(request, 'healthinsurance_prediction.html')

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def calculate_bmi(weight, height):
    if height > 0:
        height_m = height / 100  # Convert height to meters if stored in centimeters
        return weight / (height_m ** 2)
    return 0





# def register_healthpolicy01(request):
#     if request.method == "POST":    
#         num_persons = request.POST.get('num_persons')
#         office_id = request.POST.get('office_id')

#         # Perform any necessary validation on the form data
#         if not num_persons or not office_id:
#             return HttpResponse("Please fill in all the fields.")
#         return render(request,'customer/customer_health_policy_issue_02.html')  # Redirect to a new URL on success


# # views.py
# from django.shortcuts import render, redirect
# from django.urls import reverse
# from .models import Office

# def register_healthpolicy01(request):
#     if request.method == "POST":
#         num_persons = int(request.POST.get('num_persons'))
#         request.session['total_beneficiaries'] = num_persons
#         request.session['current_member'] = 1
#         return redirect('customer_health_policy_issue_02')
#     else:
#         offices = Office.objects.all()
#         return render(request, 'register_healthpolicy01.html', {'offices': offices})

# def customer_health_policy_issue_02(request):
#     if request.method == 'POST':
#         # Process the form data here and save it to database
#         current_member = request.session.get('current_member', 1)
#         if current_member < request.session['total_beneficiaries']:
#             request.session['current_member'] += 1
#             return redirect('customer_health_policy_issue_02')
#         else:
#             return redirect('final_page')  # Redirect to the final confirmation page
#     else:
#         current_member = request.session.get('current_member', 1)
#         return render(request, 'customer_health_policy_issue_02.html', {'current_member': current_member})

# Below given are the views for the health policy issue : 00

from django.shortcuts import render
from .models import HealthPlan

def health_plan_list(request):
    # Fetch all health plan records from the database
    records = HealthPlan.objects.all().values_list('id', 'ptype', 'ypremium', 'incper', 'maxamt', 'specification', 'uptoage')
    
    # Check if the records exist
    if not records:
        records = None

    # Render the template with the records
    return render(request, 'customer/customer_health_policy_issue_00.html', {'records': records})

def register_healthpolicy(request, plan_id):
    plan = get_object_or_404(HealthPlan, pk=plan_id)
    offices = Office.objects.all()
    if request.method == "POST":
        # Assume you are capturing and saving form data here
        num_persons = request.POST.get('num_persons')
        office_id = request.POST.get('office_id')
        # Process other fields and save or pass them as needed
        return redirect('register_healthpolicy01', plan_id=plan_id)
    return render(request, 'customer/customer_health_policy_issue_01.html', {
        'plan': plan,
        'offices': offices
    })
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from .models import HealthPlan, Office

def register_healthpolicy01(request, plan_id):
    plan = get_object_or_404(HealthPlan, pk=plan_id)
    offices = Office.objects.all()

    if request.method == 'POST':
        number_of_members = request.POST.get('number_of_members')
        office_id = request.POST.get('office_id')

        if number_of_members.isdigit() and int(number_of_members) > 0:
            request.session['number_of_members'] = number_of_members
            request.session['office_id'] = office_id
            return redirect('register_healthpolicy02', plan_id=plan_id)
        else:
            messages.error(request, "Please enter a valid number of persons.")

    return render(request, 'customer/customer_health_policy_issue_01.html', {
        'plan': plan,
        'offices': offices
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HealthPlan, HealthPolicy, Office
from datetime import date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@login_required
def register_healthpolicy02(request, plan_id):
    plan = get_object_or_404(HealthPlan, pk=plan_id)
    
    number_of_members = int(request.session.get('number_of_members', 1))
    office_id = request.session.get('office_id')
    
    if not office_id or not hasattr(request.user, 'customer'):
        messages.error(request, "Required information missing.")
        return redirect('error_page')
    
    office = get_object_or_404(Office, pk=office_id)
    base_amount = plan.ypremium * number_of_members
    increment_amount = base_amount * (Decimal(plan.incper) / 100)
    total_amount = base_amount + increment_amount

    if total_amount > plan.maxamt:
        total_amount = plan.maxamt

    health_policy = HealthPolicy(
        customer=request.user.customer,
        health_plan=plan,
        npersons=number_of_members,
        amount=total_amount,
        appldate=date.today(),
        penddate=date.today() + timedelta(days=365),
        office=office,
        approval=True,
        appdate=date.today()
    )
    
    try:
        health_policy.save()
        messages.success(request, "Health policy registered successfully.")
        request.session['health_policy_id'] = health_policy.id
        context = {
            'plan': plan,
            'policy_id': health_policy.id,  # Pass the policy_id to the template
            'number_of_members': number_of_members
        }
        return render(request, 'customer/customer_health_policy_issue_02.html', context)
    except Exception as e:
        logger.error(f"Failed to save health policy: {e}")
        messages.error(request, "Failed to save the policy due to an internal error.")
        return redirect('register_healthpolicy', plan_id=plan_id)




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import HMembers, HealthPolicy
from django.core.exceptions import ObjectDoesNotExist

from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def submit_member_form(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            dob = request.POST.get('dob')
            gender = request.POST.get('gender')
            weight = Decimal(request.POST.get('weight'))
            height = Decimal(request.POST.get('height'))
            photo = request.FILES.get('photo')
            health_policy_id = request.session.get('health_policy_id')

            if not all([name, dob, gender, weight, height, photo]):
                raise ValidationError("All fields are required.")

            health_policy = HealthPolicy.objects.get(id=health_policy_id)
            member = HMembers(
                name=name,
                dob=dob,
                gender=gender,
                weight=weight,
                height=height,
                photo=photo,
                health_policy=health_policy
            )
            member.full_clean()  # Validate model instance
            member.save()

            return JsonResponse({"success": True, "message": "Member details saved successfully."})
        except HealthPolicy.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid Health Policy ID"}, status=400)
        except ValidationError as ve:
            return JsonResponse({"success": False, "message": str(ve)}, status=400)
        except Exception as e:
            logger.error("Error when saving member details: %s", str(e))
            return JsonResponse({"success": False, "message": "An error occurred during submission."}, status=500)
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

from django.conf import settings
import razorpay
from django.utils import timezone

def register_healthpolicy03(request, plan_id):
    plan = get_object_or_404(HealthPlan, pk=plan_id)

    # Assuming a process to either fetch an existing HealthPolicy ID or create a new policy
    health_policy = get_object_or_404(HealthPolicy, pk=request.session.get('health_policy_id', None))
    request.session['health_policy_id'] = health_policy.pk  # Store in session

    members = HMembers.objects.filter(health_policy=health_policy)
    amount = int(health_policy.amount * 100)

    # Create a Razorpay Order
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency='INR',
        payment_capture='0'
    ))

    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler1/'

    context = {
        'plan': plan,
        'policy': health_policy,
        'members': members,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': 'INR',
        'callback_url': callback_url
    }
    return render(request, 'customer/customer_health_policy_issue_03.html', context)

from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def paymenthandler1(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    signature = request.POST.get('razorpay_signature', '')
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    # Verify the payment signature
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    try:
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if not result:
            logger.error("Signature verification failed")
            return render(request, 'paymentfail.html')

        health_policy_id = request.session.get('health_policy_id')
        if not health_policy_id:
            logger.error("Health policy ID not found in session")
            return HttpResponseBadRequest("Health Policy ID not found in session")

        health_policy = HealthPolicy.objects.get(id=health_policy_id)

        payment = Payment(
            health_policy=health_policy,
            amount=health_policy.amount,
            payment_date=timezone.now(),
            razorpay_order_id=razorpay_order_id
        )
        payment.save()

        return render(request, 'customer/customer_health_premium_payment.html')

    except HealthPolicy.DoesNotExist:
        logger.error("Health Policy not found with ID from session")
        return HttpResponseBadRequest("Health Policy not found")
    except Exception as e:
        logger.error(f"Error processing the payment: {e}")
        return HttpResponseBadRequest(f"Error in processing your payment: {e}")

   




def customer_health_premium_payment(request):
    # Your payment processing logic here
    return render(request, 'customer/customer_health_premium_payment.html')

# Health insurance Claim management

# from django.shortcuts import render
# from .models import HealthPolicy
# from django.contrib.auth.decorators import login_required

# @login_required
# def health_register_claim_00(request):
#     # Fetch health policies related to the logged-in user (assuming customer relation is through user)
#     policies = HealthPolicy.objects.filter(customer__user=request.user)
#     # Assuming there's a mechanism to identify the logged-in user
#     user = request.user
#     try:
#         policy = HealthPolicy.objects.get(customer=user.customer)  # or however the relationship is structured
#         context = {
#             'policy': policy,
#         }
#     except HealthPolicy.DoesNotExist:
#         policy = None
#         context = {
#             'error_message': 'No policy found for this customer.'
#         }    
#         return render(request, 'health_register_claim_00.html', context)

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import HealthPolicy

#@login_required
def health_register_claim_00(request):
    # Fetching health policies for the logged-in customer
    current_user = request.user
    try:
        customer = current_user.customer
        policies = HealthPolicy.objects.filter(customer=customer)
        context = {
            'policies': policies
        }
        return render(request, 'customer/health_register_claim_00.html', context)
    except AttributeError:
        # Handle the case where the user does not have an associated customer profile
        return HttpResponse("No associated customer profile found for this user.")
    
def health_register_claim_01(request, policy_id):
    policy = get_object_or_404(HealthPolicy, id=policy_id)
    return render(request, 'customer/health_register_claim_01.html', {'policy': policy})

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import HealthPolicy, ClaimRequest
from django.utils import timezone

def health_register_claim_02(request, policy_id):
    policy = get_object_or_404(HealthPolicy, id=policy_id)
    #print(policy_id)
    if request.method == 'POST':
        # Get the data from the form
        claim_amount = request.POST.get('claim_amount')
        account_number = request.POST.get('account_number')
        bank_name = request.POST.get('bank_name')
        ifsc_code = request.POST.get('ifsc_code')
        claim_date = request.POST.get('claim_date') or timezone.now().date()
        
        # Handling the file upload
        reports_file = request.FILES.get('reports')  # Get the uploaded file from request.FILES

        if not reports_file:
            return HttpResponse('Please upload a PDF report.')  # Simple validation for the file

        # Create a ClaimRequest instance and populate fields
        claim = ClaimRequest(
            health_policy=policy,
            claim_amount=claim_amount,
            reports=reports_file,  # Saving the actual file object, not a filename
            account_number=account_number,
            bank_name=bank_name,
            ifsc_code=ifsc_code,
            claim_date=claim_date
        )

        # Save the claim to the database
        claim.save()

        # Redirect to a success page
        return redirect('health_register_claim_03', policy_id = policy_id)  # Change 'some_success_url' to your actual success page's URL name

    # If it's a GET request, just display the form with policy details
    return render(request, 'customer/health_register_claim_01.html', {'policy': policy})

from django.shortcuts import render, get_object_or_404
from .models import HealthPolicy, ClaimRequest

def health_register_claim_03(request, policy_id):
    policy = get_object_or_404(HealthPolicy, id=policy_id)
    claim = ClaimRequest.objects.filter(health_policy=policy).first()
    return render(request, 'customer/health_register_claim_02.html', {'policy': policy, 'claim': claim})



# from django.shortcuts import render
# from .models import HealthPolicy
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse

# def view_health_policies(request):
#     # Fetching health policies for the logged-in customer
#     current_user = request.user
#     try:
#         customer = current_user.customer
#         health_policies = HealthPolicy.objects.filter(customer=customer)
#         context = {
#             'health_policies': health_policies
#         }
#         return render(request, 'health_policies.html', context)
#     except AttributeError:
#         # Handle the case where the user does not have an associated customer profile
#         return HttpResponse("No associated customer profile found for this user.")




# Vehicle policy application section
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User, Customer, Office, VehiclePlan, VehiclePolicy
from decimal import Decimal
import datetime
import logging

logger = logging.getLogger(__name__)

@login_required
def register_vehicle_policy(request):
    current_year = datetime.datetime.now().year
    years = range(1990, current_year + 1)
    user = request.user
    customer = getattr(user, 'customer', None)
    
    if not customer:
        logger.error(f"No customer associated with user {user.id}")
        return HttpResponse("No customer profile available.", status=400)

    offices = Office.objects.all()
    plans = VehiclePlan.objects.all()

    context = {
        'customer': customer,
        'offices': offices,
        'plans': plans,
        'years': years,
    }

    if request.method == 'POST':
        vehno = request.POST.get('t2', '').strip()
        vehvalue = Decimal(request.POST.get('t3', 0))
        vpid = request.POST.get('t4')
        enginno = request.POST.get('t5')
        chno = request.POST.get('t6')
        vehsize = request.POST.get('t7')
        vehcompany = request.POST.get('t8')
        vehpower = request.POST.get('t9')
        mfyear = int(request.POST.get('t10'))
        vehtype = request.POST.get('t11')
        officeid = request.POST.get('t12')
        vehphoto = request.FILES.get('file')

        try:
            plan = VehiclePlan.objects.get(id=vpid)
            office = Office.objects.get(officeid=officeid)

            policy_amount = calculate_policy_amount(vehvalue, plan)
            
            policy = VehiclePolicy(
                customer=customer,
                vehicle_number=vehno,
                vehicle_value=vehvalue,
                vehicle_plan=plan,
                engine_number=enginno,
                chassis_number=chno,
                vehicle_size=vehsize,
                vehicle_company=vehcompany,
                vehicle_power=vehpower,
                manufacture_year=mfyear,
                office=office,
                vehicle_photo=vehphoto,
                vehicle_type=vehtype,
                policy_amount=policy_amount,
                policy_date=datetime.date.today(),
                policy_end_date=datetime.date.today() + datetime.timedelta(days=365)
            )
            policy.save()
            logger.info(f"Vehicle Policy for {vehno} created successfully.")
            return redirect('policy_success')
        except (VehiclePlan.DoesNotExist, Office.DoesNotExist, ValueError) as e:
            logger.error(f"Error processing your request: {e}")
            return HttpResponse(f"Error processing your request: {e}", status=400)
    else:
        return render(request, 'customer/customer_vehicle_policyissue.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import VehiclePolicy
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
 
 
# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from .models import VehiclePolicy

# @login_required
# def policy_success(request):
#     customer = request.user.customer
#     vehicle_policy = VehiclePolicy.objects.filter(customer=customer).order_by('-policy_date', '-id').first()
#     if not vehicle_policy:
#         return render(request, 'error.html', {'message': 'No vehicle policy found for this customer.'})
    
#     # Store the vehicle_policy ID in session
#     request.session['vehicle_policy_id'] = vehicle_policy.id
    
#     amt=int(vehicle_policy.policy_amount)

#     # Specify the amount (in the smallest currency unit, i.e., paise for INR)
#     amount = amt  # e.g., Rs. 200.00 should be 20000 paise

#     # Create a Razorpay Order
#     razorpay_order = razorpay_client.order.create(dict(
#         amount=amount, 
#         currency='INR', 
#         payment_capture='0'
#     ))

#     # Get the order ID from Razorpay response
#     razorpay_order_id = razorpay_order['id']
#     callback_url = '/paymenthandler/'  # This should be the actual URL for handling the payment callback

#     context = {
#         'customer': customer,
#         'vehicle_policy': vehicle_policy,
#         'plan': vehicle_policy.vehicle_plan,
#         'razorpay_order_id': razorpay_order_id,
#         'razorpay_merchant_key': settings.RAZOR_KEY_ID,
#         'razorpay_amount': amount,
#         'currency': 'INR',
#         'callback_url': callback_url
#     }

#     return render(request, 'customer/customer_vehicle_policyissue_successful.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import VehiclePolicy
import qrcode
from io import BytesIO
from base64 import b64encode

@login_required
def policy_success(request):
    customer = request.user.customer
    vehicle_policy = VehiclePolicy.objects.filter(customer=customer).order_by('-policy_date', '-id').first()
    if not vehicle_policy:
        return render(request, 'error.html', {'message': 'No vehicle policy found for this customer.'})
    
    # Generate QR code for the vehicle policy
    qr_data = f"User: {customer.user.get_full_name()}\nPolicy Number: {vehicle_policy.id}\nVehicle Number: {vehicle_policy.vehicle_number}\nPolicy Amount: {vehicle_policy.policy_amount}\nPolicy End Date: {vehicle_policy.policy_end_date}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_base64 = b64encode(img_buffer.getvalue()).decode('utf-8')

    context = {
        'customer': customer,
        'vehicle_policy': vehicle_policy,
        'qr_code': img_base64,
    }
    return render(request, 'customer/customer_vehicle_premium_payment.html', context)



def calculate_policy_amount(vehvalue, plan):
    depreciation_factor = Decimal(plan.depreciation / 100)
    plan_percentage = Decimal(plan.Ppercentage / 100)  # Changed from 'percentage' to 'Ppercentage'
    return (vehvalue - (vehvalue * depreciation_factor)) * (1 + plan_percentage)

def customer_vehicle_premium_payment(request):
    # Your payment processing logic here
    return render(request, 'customer/customer_vehicle_premium_payment.html')

# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import VehiclePolicy, Payment
import logging
from django.utils import timezone

# Assuming razorpay_client is properly initialized and imported
logger = logging.getLogger(__name__)

@csrf_exempt
def paymenthandler(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")
    

    payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    signature = request.POST.get('razorpay_signature', '')
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        # Verify the payment signature
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if not result:
            logger.error("Signature verification failed")
            return render(request, 'paymentfail.html')

        # Retrieve vehicle policy using session
        vehicle_policy_id = request.session.get('vehicle_policy_id')
        if not vehicle_policy_id:
            logger.error("Vehicle policy ID not found in session")
            return HttpResponseBadRequest("Vehicle Policy ID not found in session")

        vehicle_policy = VehiclePolicy.objects.get(id=vehicle_policy_id)

        # Create and save the payment object
        payment = Payment(
            vehicle_policy=vehicle_policy,
            amount=vehicle_policy.policy_amount,
            payment_date=timezone.now(),
            razorpay_order_id=razorpay_order_id
        )
        payment.save()

        return render(request, 'customer/customer_vehicle_premium_payment.html')

    except VehiclePolicy.DoesNotExist:
        logger.error("Vehicle Policy not found with ID from session")
        return HttpResponseBadRequest("Vehicle Policy not found")
    except KeyError as e:
        logger.error(f"Missing key in POST data or session: {e}")
        return HttpResponseBadRequest(f"Bad request: Missing data {e}")
    except Exception as e:
        logger.error(f"Error processing the payment: {e}")
        return HttpResponseBadRequest(f"Error in processing your payment: {e}")

from .models import VehiclePolicy
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import qrcode
from io import BytesIO

@login_required
def generate_policy_qr(request):
    # Retrieve Customer instance directly from User
    try:
        customer = request.user.customer
    except AttributeError:
        return HttpResponse("No customer profile associated with this user.", status=404)

    # Get the last vehicle policy for this customer
    vehicle_policy = VehiclePolicy.objects.filter(customer=customer).order_by('-policy_date').first()
    
    if not vehicle_policy:
        return HttpResponse("No vehicle policy found for this customer.", status=404)

    # Fetch user's full name from the Customer model
    user_name = f"{customer.first_name} {customer.last_name}".strip()

    # Generate QR code data with user's name and policy details
    qr_data = f"User: {user_name}\nPolicy Number: {vehicle_policy.id}\nVehicle Number: {vehicle_policy.vehicle_number}\nVehicle Value: {vehicle_policy.vehicle_value}\nPolicy Amount: {vehicle_policy.policy_amount}\nPolicy End Date: {vehicle_policy.policy_end_date}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Save image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    # Return the image as a response
    return HttpResponse(buffer, content_type="image/png")


# Vehicle claim management

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import VehiclePolicy

#@login_required
def vehicle_register_claim_00(request):
    # Fetching health policies for the logged-in customer
    current_user = request.user
    try:
        customer = current_user.customer
        policies = VehiclePolicy.objects.filter(customer=customer)
        context = {
            'policies': policies
        }
        return render(request, 'customer/vehicle_register_claim_00.html', context)
    except AttributeError:
        # Handle the case where the user does not have an associated customer profile
        return HttpResponse("No associated customer profile found for this user.")
    
def vehicle_register_claim_01(request, policy_id):
    policy = get_object_or_404(VehiclePolicy, id=policy_id)
    return render(request, 'customer/vehicle_register_claim_01.html', {'policy': policy})

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import VehiclePolicy, ClaimRequest
from django.utils import timezone

def vehicle_register_claim_02(request, policy_id):
    policy = get_object_or_404(VehiclePolicy, id=policy_id)
    #print(policy_id)
    if request.method == 'POST':
        # Get the data from the form
        claim_amount = request.POST.get('claim_amount')
        account_number = request.POST.get('account_number')
        bank_name = request.POST.get('bank_name')
        ifsc_code = request.POST.get('ifsc_code')
        claim_date = request.POST.get('claim_date') or timezone.now().date()
        
        # Handling the file upload
        reports_file = request.FILES.get('reports')  # Get the uploaded file from request.FILES

        if not reports_file:
            return HttpResponse('Please upload a PDF report.')  # Simple validation for the file

        # Create a ClaimRequest instance and populate fields
        claim = ClaimRequest(
            vehicle_policy=policy,
            claim_amount=claim_amount,
            reports=reports_file,  # Saving the actual file object, not a filename
            account_number=account_number,
            bank_name=bank_name,
            ifsc_code=ifsc_code,
            claim_date=claim_date
        )

        # Save the claim to the database
        claim.save()

        # Redirect to a success page
        return redirect('vehicle_register_claim_03', policy_id = policy_id)  # Change 'some_success_url' to your actual success page's URL name

    # If it's a GET request, just display the form with policy details
    return render(request, 'customer/vehicle_register_claim_01.html', {'policy': policy})

from django.shortcuts import render, get_object_or_404
from .models import VehiclePolicy, ClaimRequest

def vehicle_register_claim_03(request, policy_id):
    policy = get_object_or_404(VehiclePolicy, id=policy_id)
    claim = ClaimRequest.objects.filter(vehicle_policy=policy).first()
    return render(request, 'customer/vehicle_register_claim_02.html', {'policy': policy, 'claim': claim})

# Staff Claim Approval

from django.views.generic import ListView
from .models import ClaimRequest
from django.db.models import Q

class ClaimListView(ListView):
    model = ClaimRequest
    template_name = 'staff/staff_list_claim_requests.html'
    context_object_name = 'claims'
    paginate_by = 10  # Adjust pagination as needed

    def get_queryset(self):
        # This method is used to customize the query that populates 'claims'
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "")  # Retrieves the search query from the request

        if query:
            queryset = queryset.filter(
                Q(vehicle_policy__policy_number=query) | Q(health_policy__policy_number=query)
            )
        return queryset.order_by('-claim_date')  # Example of default sorting by claim date

    # Optionally, you could add a method to add additional context to the template
    # such as showing the current search term
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get("q", "")
        return context

from django.shortcuts import render, get_object_or_404, redirect
from .models import ClaimRequest

def claim_verification(request, claim_id):
    # Retrieve the claim object based on the passed claim_id
    claim = get_object_or_404(ClaimRequest, pk=claim_id)

    # Check the type of the policy linked to the claim
    if claim.health_policy_id:
        # If it is a health policy, redirect to the health policy approval view
        return redirect('staff_health_claim_approval_00', claim_id=claim_id)
    elif claim.vehicle_policy_id:
        # If it is a vehicle policy, redirect to the vehicle policy approval view
        return redirect('staff_vehicle_claim_approval_00', claim_id=claim_id)
    else:
        # Optional: Redirect or render a generic error page if no policy is linked
        template_name = 'staff/staff_list_claim_requests.html'  # Assuming this is a fallback template
        return render(request, template_name)


from django.shortcuts import render, get_object_or_404
from .models import ClaimRequest, VehiclePolicy, Customer

def staff_vehicle_claim_approval_00(request, claim_id):
    claim = get_object_or_404(ClaimRequest, pk=claim_id, vehicle_policy__isnull=False)
    vehicle_policy = claim.vehicle_policy
    customer = vehicle_policy.customer

    context = {
        'claim': claim,
        'vehicle_policy': vehicle_policy,
        'customer': customer
    }
    return render(request, 'staff/staff_vehicle_claim_approval_00.html', context)


from django.shortcuts import render, get_object_or_404
from .models import ClaimRequest, HealthPolicy, Customer

def staff_health_claim_approval_00(request, claim_id):
    claim = get_object_or_404(ClaimRequest, pk=claim_id, health_policy__isnull=False)
    health_policy = claim.health_policy
    customer = health_policy.customer

    context = {
        'claim': claim,
        'health_policy': health_policy,
        'customer': customer
    }
    return render(request, 'staff/staff_health_claim_approval_00.html', context)


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from .models import ClaimApproval, ClaimRequest
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
def staff_health_claim_approval_01(request, claim_request_id):
    try:
        claim_request = ClaimRequest.objects.get(id=claim_request_id)
    except ClaimRequest.DoesNotExist:
        return HttpResponse(_("Claim request not found."), status=404)
    # staff_member = request.user
    staff_member = request.user
    if not staff_member:
        logger.error(f"No staff member associated with user {request.user.id}")
        return HttpResponse("No associated staff member found.", status=400)

    if request.method == 'POST':
        approval_status = request.POST.get('approval_status')
        comment = request.POST.get('comment')
        approved_amount = request.POST.get('approved_amount') or None
        approval_date = date.today()

        claim_approval = ClaimApproval(
            claim_request=claim_request,
            approval_status=approval_status,
            comment=comment,
            approved_amount=approved_amount,
            approval_date=approval_date,
            staff=staff_member  # Ensure this is a Staff instance
        )
        claim_approval.save()
        return redirect('staff_claim_list')    
    else:
        return render(request, 'your_template_name.html', {'claim_request': claim_request})

@login_required
def staff_vehicle_claim_approval_01(request, claim_request_id):
    try:
        claim_request = ClaimRequest.objects.get(id=claim_request_id)
    except ClaimRequest.DoesNotExist:
        return HttpResponse(_("Claim request not found."), status=404)

    staff_member = request.user
    if not staff_member:
        logger.error(f"No staff member associated with user {request.user.id}")
        return HttpResponse("No associated staff member found.", status=400)

    if request.method == 'POST':
        approval_status = request.POST.get('approval_status')
        comment = request.POST.get('comment')
        approved_amount = request.POST.get('approved_amount') or None
        approval_date = date.today()

        claim_approval = ClaimApproval(
            claim_request=claim_request,
            approval_status=approval_status,
            comment=comment,
            approved_amount=approved_amount,
            approval_date=approval_date,
            staff=staff_member  # Ensure this is a Staff instance
        )
        claim_approval.save()
        return redirect('staff_claim_list')
    else:
        return render(request, 'your_template_name.html', {'claim_request': claim_request})


# Customer check policy status

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import HealthPolicy

@login_required
def customer_health_policy_status_00(request):
    current_user = request.user
    # Assuming there's a relationship through `customer` field to user
    health_policies = HealthPolicy.objects.filter(customer__user=current_user)
    return render(request, 'customer/customer_health_policy_status_00.html', {'health_policies': health_policies})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import VehiclePolicy

@login_required
def customer_vehicle_policy_status_00(request):
    current_user = request.user
    # Assuming there's a relationship through `customer` field to user
    vehicle_policies = VehiclePolicy.objects.filter(customer__user=current_user)
    return render(request, 'customer/customer_vehicle_policy_status_00.html', {'vehicle_policies': vehicle_policies})

# Customer checks the policy status

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ClaimRequest, ClaimApproval

@login_required
def customer_health_claim_status_00(request):
    current_user = request.user
    if current_user.role == User.Role.CUSTOMER:
        customer = current_user.customer
        health_claims = ClaimRequest.objects.filter(health_policy__customer=customer).prefetch_related('approvals')

        # Organizing claim data with most recent approval
        claims_with_latest_approval = []
        for claim in health_claims:
            latest_approval = claim.approvals.order_by('-approval_date').first()
            claims_with_latest_approval.append((claim, latest_approval))
    else:
        claims_with_latest_approval = []

    return render(request, 'customer/customer_health_claim_status_00.html', {
        'claims_with_latest_approval': claims_with_latest_approval
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ClaimRequest, Staff, User

@login_required
def customer_vehicle_claim_status_00(request):
    customer = request.user.customer
    claims = ClaimRequest.objects.filter(vehicle_policy__customer=customer).select_related('vehicle_policy')
    
    claims_with_approvals = []
    for claim in claims:
        latest_approval = claim.approvals.order_by('-approval_date').first()
        
        
        
        staff = None
        if latest_approval:
           
            staff = Staff.objects.filter(user=latest_approval.staff).first()
        claims_with_approvals.append((claim, latest_approval, staff))
    
    context = {
        'claims_with_approvals': claims_with_approvals
    }
    return render(request, 'customer/customer_vehicle_claim_status_00.html', context)








from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
import requests
import json
from .models import Agent

def agents_map(request):
    agents = Agent.objects.all()
    agents_data = []

    headers = {
        'User-Agent': 'YourAppName/1.0 (your_email@example.com)'
    }

    for agent in agents:
        query = agent.place.replace(" ", "+")
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        response = requests.get(url, headers=headers)

        try:
            data = response.json()
            if data:
                latitude = data[0]['lat']
                longitude = data[0]['lon']
                agents_data.append({
                    'name': agent.name,
                    'address': agent.address,
                    'phone': agent.phone,
                    'photo_url': agent.photo.url if agent.photo else None,
                    'latitude': latitude,
                    'longitude': longitude,
                })
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON from response: {e}")
            continue

    context = {
        'agents': json.dumps(agents_data, cls=DjangoJSONEncoder),
    }
    return render(request, 'customer/agents_map.html', context)

from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import VehiclePolicy  # Make sure this import correctly reflects your app and model structure

def generate_policy_pdf(request, policy_id):
    try:
        vehicle_policy = VehiclePolicy.objects.get(id=policy_id)
    except VehiclePolicy.DoesNotExist:
        return HttpResponse("Policy not found")

    # Access the Customer object related to the VehiclePolicy
    customer = vehicle_policy.customer

    # Create a PDF document
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, 'Insurance Policy Receipt')

    # Add policy details to the PDF
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, f'Policy Number: {vehicle_policy.id}')
    p.drawString(100, 730, f'Vehicle Number: {vehicle_policy.vehicle_number}')
    p.drawString(100, 710, f'Policy Amount: ₹{vehicle_policy.policy_amount}')
    p.drawString(100, 690, f'Policy Start Date: {vehicle_policy.policy_date}')  # Correct field name for policy date
    p.drawString(100, 670, f'Policy End Date: {vehicle_policy.policy_end_date}')
    p.drawString(100, 650, f'Issued To: {customer.first_name} {customer.last_name}')  # Accessing customer's full name

    # Optionally, include the customer's image if available
    if customer.image:
        customer_image_path = customer.image.path
        p.drawInlineImage(customer_image_path, 450, 650, width=100, height=100)

    p.save()

    # Move the buffer's pointer to the beginning
    buffer.seek(0)

    # Create an HttpResponse object with the PDF data
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Policy_{vehicle_policy.id}_Receipt.pdf'

    buffer.close()

    return response








from django.shortcuts import render
from .models import VehiclePolicy
from datetime import date

def vehicle_policies_list(request):
    customer = request.user.customer
    policies = VehiclePolicy.objects.filter(customer=customer)
    today = date.today()
    return render(request, 'customer/vehicle_policies.html', {'policies': policies, 'today': today})



from datetime import timedelta
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import now
from .models import VehiclePolicy
from django.contrib import messages
from dateutil.relativedelta import relativedelta  # For adding months/years to a date

def renew_policy(request, policy_id):
        policy = get_object_or_404(VehiclePolicy, id=policy_id)
  
        # Calculate new premium amount
        current_value = policy.vehicle_value
        print(current_value,"kkkkkkkkkk")
        depreciation = policy.vehicle_plan.depreciation
        premium_percentage = policy.vehicle_plan.Ppercentage

        # Apply depreciation and calculate new vehicle value
        new_value = current_value - (current_value * (depreciation / 100))
        new_premium = new_value * (premium_percentage / 100)

        # Update the policy amount
        policy.policy_amount = new_premium

        # Extend the policy by one year
        policy.policy_end_date += relativedelta(years=1)

        # Save the updated policy
        policy.save()

        # Redirect to the policies list with a success message
        messages.success(request, 'Policy renewed successfully!')


        return redirect('vehicle_policies_list')


def renew_health(request):
    customer = request.user.customer
    policies = HealthPolicy.objects.filter(customer=customer)
    today = date.today()
    return render(request, 'customer/health_policies.html', {'policies': policies, 'today': today})


from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from datetime import timedelta
from .models import HealthPolicy

def renew_policy_health0(request, policy_id):
    policy = get_object_or_404(HealthPolicy, pk=policy_id)
    
    policy.amount += 300
    policy.penddate += timedelta(days=365)
    policy.save()
    message = "Policy renewed successfully!"
    
    return redirect('renew_health')


# Forgot Password


class RequestResetEmailView(View):
      def get(self,request):
            return render(request,'authentication/request-reset-email.html')
      
      def post(self,request):
            email=request.POST['email']
            user=User.objects.filter(email=email)

            if user.exists():
                  current_site=get_current_site(request)
                  email_sub="[Reset your Password]"
                  message=render_to_string('authentication/reset-user-password.html',{
                        
                        'domain':current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                        'token':PasswordResetTokenGenerator().make_token(user[0])
                  })

                  email_message=EmailMessage(email_sub,message,settings.EMAIL_HOST_USER,[email])
                  EmailThread(email_message).start()
                  messages.info(request,"we sent instructions to how reset password")
                  return render(request,'authentication/request-reset-email.html')



            
class SetNewPassword(View):
       def get(self,request,uidb64,token):
              
              context={
                  'uidb64':uidb64,
                  'token':token
               }
              try:
                  user_id=force_str(urlsafe_base64_decode(uidb64))
                  user=User.objects.get(pk=user_id)
                  if not PasswordResetTokenGenerator().check_token(user,token):
                        messages.warning(request,"password reset link is in valid")
                        return render(request,'authentication/request-reset-email.html')
              except DjangoUnicodeDecodeError as identifier:
                    pass

              return render(request,'authentication/set-new-password.html',context)
      
       def post(self,request,uidb64,token):
              context={
                   'uidb64':uidb64,
                  'token':token
              
                }
              password=request.POST['password']
              confirm_password=request.POST['confirm_password']
              if password!=confirm_password:
                    messages.warning(request,"password is not matching")
                    return render(request,'authentication/set-new-password.html',context)
              try:
                    user_id=force_str(urlsafe_base64_decode(uidb64))
                    user=User.objects.get(pk=user_id)
                    user.set_password(password)
                    user.save()
                    messages.success(request,"Password reset sucess. you can login with new password")
                    return redirect('/handlelogin')
              
              except DjangoUnicodeDecodeError as identifier:
                    messages.error(request,"Something went wrong")
                    return redirect('authentication/set-new-password.html',context)
              return render(request,'authentication/set-new-password.html',context)
       
# Staff Policy Issue section

def staff_list_customers(request):
    query = request.GET.get('q', '')
    if query:
        customers = Customer.objects.filter(
            user__first_name__icontains=query) | Customer.objects.filter(
            user__last_name__icontains=query)
    else:
        customers = Customer.objects.all()
    return render(request, 'staff/staff_list_customers.html', {'customers': customers})


from django.shortcuts import render
from .models import HealthPlan

def staff_health_plan_list(request,customer_id):
    
    # Store the customer_id in the session

    request.session['customer_id'] = customer_id

    # Fetch all health plan records from the database
    
    records = HealthPlan.objects.all().values_list('id', 'ptype', 'ypremium', 'incper', 'maxamt', 'specification', 'uptoage')
    
    # Check if the records exist
    if not records:
        records = None

    # Render the template with the records
    return render(request, 'staff/staff_health_policy_issue_00.html', {'records': records})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import HealthPlan, Office, Staff, Customer, HealthPolicy
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def staff_register_healthpolicy(request, plan_id):
    if not hasattr(request.user, 'staff'):
        messages.error(request, "You are not authorized to perform this action.")
        #return redirect('error_page')

    plan = get_object_or_404(HealthPlan, pk=plan_id)
    offices = Office.objects.all()
    if request.method == "POST":
        num_persons = request.POST.get('num_persons')
        office_id = request.POST.get('office_id')
        request.session['num_persons'] = num_persons  # Store number of persons in the session
        request.session['office_id'] = office_id  # Store office_id in the session
        return redirect('staff_register_healthpolicy01', plan_id=plan_id)
    return render(request, 'staff/staff_health_policy_issue_01.html', {
        'plan': plan,
        'offices': offices
    })

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from .models import HealthPlan, Office

def staff_register_healthpolicy01(request, plan_id):
    plan = get_object_or_404(HealthPlan, pk=plan_id)
    offices = Office.objects.all()

    if request.method == 'POST':
        number_of_members = request.POST.get('number_of_members')
        office_id = request.POST.get('office_id')

        if number_of_members.isdigit() and int(number_of_members) > 0:
            request.session['number_of_members'] = number_of_members
            request.session['office_id'] = office_id
            return redirect('staff_register_healthpolicy02', plan_id=plan_id)
        else:
            messages.error(request, "Please enter a valid number of persons.")

    return render(request, 'staff/staff_health_policy_issue_01.html', {
        'plan': plan,
        'offices': offices
    })

def staff_register_healthpolicy02(request, plan_id):
    if not hasattr(request.user, 'staff'):
        messages.error(request, "You are not authorized to perform this action.")
        #return redirect('error_page')

    plan = get_object_or_404(HealthPlan, pk=plan_id)
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, id=customer_id)
    staff_member = request.user.staff
    num_persons = int(request.session.get('num_persons', 1))
    office_id = request.session.get('office_id')
    office = get_object_or_404(Office, pk=office_id)

    amount = plan.ypremium * num_persons
    amount += amount * (Decimal(plan.incper) / 100)
    amount = min(amount, plan.maxamt)  # Cap the amount to the maximum allowed

    health_policy = HealthPolicy(
        customer=customer,
        # agent=None,  # Assume no agent involved, modify as necessary
        health_plan=plan,
        npersons=num_persons,
        amount=amount,
        appldate=now(),
        penddate=now() + timedelta(days=365),
        office=office,
        approval=True,
        appdate=now(),
        staff=staff_member
    )
    health_policy.save()
    messages.success(request, "Health policy registered successfully.")
    return redirect('some_followup_view')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import HMembers, HealthPolicy
from django.core.exceptions import ObjectDoesNotExist

from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def staff_submit_member_form(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            dob = request.POST.get('dob')
            gender = request.POST.get('gender')
            weight = Decimal(request.POST.get('weight'))
            height = Decimal(request.POST.get('height'))
            photo = request.FILES.get('photo')
            health_policy_id = request.session.get('health_policy_id')

            if not all([name, dob, gender, weight, height, photo]):
                raise ValidationError("All fields are required.")

            health_policy = HealthPolicy.objects.get(id=health_policy_id)
            member = HMembers(
                name=name,
                dob=dob,
                gender=gender,
                weight=weight,
                height=height,
                photo=photo,
                health_policy=health_policy
            )
            member.full_clean()  # Validate model instance
            member.save()

            return JsonResponse({"success": True, "message": "Member details saved successfully."})
        except HealthPolicy.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid Health Policy ID"}, status=400)
        except ValidationError as ve:
            return JsonResponse({"success": False, "message": str(ve)}, status=400)
        except Exception as e:
            logger.error("Error when saving member details: %s", str(e))
            return JsonResponse({"success": False, "message": "An error occurred during submission."}, status=500)
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

from django.conf import settings
import razorpay
from django.utils import timezone

def staff_register_healthpolicy03(request, plan_id):
    plan = get_object_or_404(HealthPlan, pk=plan_id)

    # Assuming a process to either fetch an existing HealthPolicy ID or create a new policy
    health_policy = get_object_or_404(HealthPolicy, pk=request.session.get('health_policy_id', None))
    request.session['health_policy_id'] = health_policy.pk  # Store in session

    members = HMembers.objects.filter(health_policy=health_policy)
    amount = int(health_policy.amount * 100)

    # Create a Razorpay Order
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency='INR',
        payment_capture='0'
    ))

    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler02/'

    context = {
        'plan': plan,
        'policy': health_policy,
        'members': members,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': 'INR',
        'callback_url': callback_url
    }
    return render(request, 'staff/staff_health_policy_issue_03.html', context)

from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def paymenthandler02(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    signature = request.POST.get('razorpay_signature', '')
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    # Verify the payment signature
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    try:
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if not result:
            logger.error("Signature verification failed")
            return render(request, 'paymentfail.html')

        health_policy_id = request.session.get('health_policy_id')
        if not health_policy_id:
            logger.error("Health policy ID not found in session")
            return HttpResponseBadRequest("Health Policy ID not found in session")

        health_policy = HealthPolicy.objects.get(id=health_policy_id)

        payment = Payment(
            health_policy=health_policy,
            amount=health_policy.amount,
            payment_date=timezone.now(),
            razorpay_order_id=razorpay_order_id
        )
        payment.save()

        return render(request, 'staff/staff_health_premium_payment.html')

    except HealthPolicy.DoesNotExist:
        logger.error("Health Policy not found with ID from session")
        return HttpResponseBadRequest("Health Policy not found")
    except Exception as e:
        logger.error(f"Error processing the payment: {e}")
        return HttpResponseBadRequest(f"Error in processing your payment: {e}")



    # Staff Vehicle Policy Application Handle

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User, Customer, Staff, Office, VehiclePlan, VehiclePolicy
from decimal import Decimal
import datetime

@login_required
def staff_register_vehicle_policy(request, customer_id):
    if request.user.role != User.Role.STAFF:
        return HttpResponse("Unauthorized", status=403)

    current_year = datetime.datetime.now().year
    years = range(1990, current_year + 1)
    staff = get_object_or_404(Staff, user=request.user)  # Assuming staff is logged in
    customer = get_object_or_404(Customer, id=customer_id)  # Get customer from the passed ID

    offices = Office.objects.all()
    plans = VehiclePlan.objects.all()

    context = {
        'customer': customer,
        'staff': staff,
        'offices': offices,
        'plans': plans,
        'years': years,
    }

    if request.method == 'POST':
        # Retrieve form data
        vehicle_number = request.POST.get('vehicle_number').strip()
        vehicle_value = Decimal(request.POST.get('vehicle_value', 0))
        plan_id = request.POST.get('plan_id')
        engine_number = request.POST.get('engine_number')
        chassis_number = request.POST.get('chassis_number')
        vehicle_size = request.POST.get('vehicle_size')
        vehicle_company = request.POST.get('vehicle_company')
        vehicle_power = request.POST.get('vehicle_power')
        manufacture_year = int(request.POST.get('manufacture_year'))
        vehicle_type = request.POST.get('vehicle_type')
        office_id = request.POST.get('office_id')
        vehicle_photo = request.FILES.get('file')
        
        # Additional error handling might be needed here
        plan = VehiclePlan.objects.get(id=plan_id)
        office = Office.objects.get(id=office_id)
        policy_amount = calculate_policy_amount(vehicle_value, plan)

        # Create the policy
        policy = VehiclePolicy(
            customer=customer,
            staff=staff,
            vehicle_number=vehicle_number,
            vehicle_value=vehicle_value,
            vehicle_plan=plan,
            engine_number=engine_number,
            chassis_number=chassis_number,
            vehicle_size=vehicle_size,
            vehicle_company=vehicle_company,
            vehicle_power=vehicle_power,
            manufacture_year=manufacture_year,
            office=office,
            vehicle_photo=vehicle_photo,
            vehicle_type=vehicle_type,
            policy_amount=policy_amount,
            policy_date=datetime.date.today(),
            policy_end_date=datetime.date.today() + datetime.timedelta(days=365)
        )
        policy.save()
        return redirect('staff-policy_success')
    else:
        return render(request, 'staff/staff_register_vehicle_policy.html', context)

# Calculate Policy Amount Function
def calculate_policy_amount(vehvalue, plan):
    depreciation_factor = Decimal(plan.depreciation / 100)
    plan_percentage = Decimal(plan.percentage / 100)  # Adjust field name as needed
    return (vehvalue - (vehvalue * depreciation_factor)) * (1 + plan_percentage)

from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
 
 
# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from .models import VehiclePolicy

# @login_required
# def policy_success(request):
#     customer = request.user.customer
#     vehicle_policy = VehiclePolicy.objects.filter(customer=customer).order_by('-policy_date', '-id').first()
#     if not vehicle_policy:
#         return render(request, 'error.html', {'message': 'No vehicle policy found for this customer.'})
    
#     # Store the vehicle_policy ID in session
#     request.session['vehicle_policy_id'] = vehicle_policy.id
    
#     amt=int(vehicle_policy.policy_amount)

#     # Specify the amount (in the smallest currency unit, i.e., paise for INR)
#     amount = amt  # e.g., Rs. 200.00 should be 20000 paise

#     # Create a Razorpay Order
#     razorpay_order = razorpay_client.order.create(dict(
#         amount=amount, 
#         currency='INR', 
#         payment_capture='0'
#     ))

#     # Get the order ID from Razorpay response
#     razorpay_order_id = razorpay_order['id']
#     callback_url = '/paymenthandler/'  # This should be the actual URL for handling the payment callback

#     context = {
#         'customer': customer,
#         'vehicle_policy': vehicle_policy,
#         'plan': vehicle_policy.vehicle_plan,
#         'razorpay_order_id': razorpay_order_id,
#         'razorpay_merchant_key': settings.RAZOR_KEY_ID,
#         'razorpay_amount': amount,
#         'currency': 'INR',
#         'callback_url': callback_url
#     }

#     return render(request, 'customer/customer_vehicle_policyissue_successful.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import VehiclePolicy
import qrcode
from io import BytesIO
from base64 import b64encode

@login_required
def staff_policy_success(request):
    customer = request.user.customer
    vehicle_policy = VehiclePolicy.objects.filter(customer=customer).order_by('-policy_date', '-id').first()
    if not vehicle_policy:
        return render(request, 'error.html', {'message': 'No vehicle policy found for this customer.'})
    
    # Generate QR code for the vehicle policy
    qr_data = f"User: {customer.user.get_full_name()}\nPolicy Number: {vehicle_policy.id}\nVehicle Number: {vehicle_policy.vehicle_number}\nPolicy Amount: {vehicle_policy.policy_amount}\nPolicy End Date: {vehicle_policy.policy_end_date}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_base64 = b64encode(img_buffer.getvalue()).decode('utf-8')

    context = {
        'customer': customer,
        'vehicle_policy': vehicle_policy,
        'qr_code': img_base64,
    }
    return render(request, 'staff/staff_vehicle_premium_payment.html', context)



def calculate_policy_amount(vehvalue, plan):
    depreciation_factor = Decimal(plan.depreciation / 100)
    plan_percentage = Decimal(plan.Ppercentage / 100)  # Changed from 'percentage' to 'Ppercentage'
    return (vehvalue - (vehvalue * depreciation_factor)) * (1 + plan_percentage)

def staff_vehicle_premium_payment(request):
    # Your payment processing logic here
    return render(request, 'staff/staff_vehicle_premium_payment.html')

# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import VehiclePolicy, Payment
import logging
from django.utils import timezone

# Assuming razorpay_client is properly initialized and imported
logger = logging.getLogger(__name__)

@csrf_exempt
def paymenthandler00(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")
    

    payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    signature = request.POST.get('razorpay_signature', '')
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        # Verify the payment signature
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if not result:
            logger.error("Signature verification failed")
            return render(request, 'paymentfail.html')

        # Retrieve vehicle policy using session
        vehicle_policy_id = request.session.get('vehicle_policy_id')
        if not vehicle_policy_id:
            logger.error("Vehicle policy ID not found in session")
            return HttpResponseBadRequest("Vehicle Policy ID not found in session")

        vehicle_policy = VehiclePolicy.objects.get(id=vehicle_policy_id)

        # Create and save the payment object
        payment = Payment(
            vehicle_policy=vehicle_policy,
            amount=vehicle_policy.policy_amount,
            payment_date=timezone.now(),
            razorpay_order_id=razorpay_order_id
        )
        payment.save()

        return render(request, 'staff/staff_vehicle_premium_payment.html')

    except VehiclePolicy.DoesNotExist:
        logger.error("Vehicle Policy not found with ID from session")
        return HttpResponseBadRequest("Vehicle Policy not found")
    except KeyError as e:
        logger.error(f"Missing key in POST data or session: {e}")
        return HttpResponseBadRequest(f"Bad request: Missing data {e}")
    except Exception as e:
        logger.error(f"Error processing the payment: {e}")
        return HttpResponseBadRequest(f"Error in processing your payment: {e}")

from .models import VehiclePolicy
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import qrcode
from io import BytesIO

@login_required
def staff_generate_policy_qr(request):
    # Retrieve Customer instance directly from User
    try:
        customer = request.user.customer
    except AttributeError:
        return HttpResponse("No customer profile associated with this user.", status=404)

    # Get the last vehicle policy for this customer
    vehicle_policy = VehiclePolicy.objects.filter(customer=customer).order_by('-policy_date').first()
    
    if not vehicle_policy:
        return HttpResponse("No vehicle policy found for this customer.", status=404)

    # Fetch user's full name from the Customer model
    user_name = f"{customer.first_name} {customer.last_name}".strip()

    # Generate QR code data with user's name and policy details
    qr_data = f"User: {user_name}\nPolicy Number: {vehicle_policy.id}\nVehicle Number: {vehicle_policy.vehicle_number}\nVehicle Value: {vehicle_policy.vehicle_value}\nPolicy Amount: {vehicle_policy.policy_amount}\nPolicy End Date: {vehicle_policy.policy_end_date}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Save image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    # Return the image as a response
    return HttpResponse(buffer, content_type="image/png")

   


from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import VehiclePolicy  # Make sure this import correctly reflects your app and model structure

def staff_generate_policy_pdf(request, policy_id):
    try:
        vehicle_policy = VehiclePolicy.objects.get(id=policy_id)
    except VehiclePolicy.DoesNotExist:
        return HttpResponse("Policy not found")

    # Access the Customer object related to the VehiclePolicy
    customer = vehicle_policy.customer

    # Create a PDF document
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, 'Insurance Policy Receipt')

    # Add policy details to the PDF
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, f'Policy Number: {vehicle_policy.id}')
    p.drawString(100, 730, f'Vehicle Number: {vehicle_policy.vehicle_number}')
    p.drawString(100, 710, f'Policy Amount: ₹{vehicle_policy.policy_amount}')
    p.drawString(100, 690, f'Policy Start Date: {vehicle_policy.policy_date}')  # Correct field name for policy date
    p.drawString(100, 670, f'Policy End Date: {vehicle_policy.policy_end_date}')
    p.drawString(100, 650, f'Issued To: {customer.first_name} {customer.last_name}')  # Accessing customer's full name

    # Optionally, include the customer's image if available
    if customer.image:
        customer_image_path = customer.image.path
        p.drawInlineImage(customer_image_path, 450, 650, width=100, height=100)

    p.save()

    # Move the buffer's pointer to the beginning
    buffer.seek(0)

    # Create an HttpResponse object with the PDF data
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Policy_{vehicle_policy.id}_Receipt.pdf'

    buffer.close()

    return response


# Agent handling policy application

def agent_list_customers(request):
    query = request.GET.get('q', '')
    if query:
        customers = Customer.objects.filter(
            user__first_name__icontains=query) | Customer.objects.filter(
            user__last_name__icontains=query)
    else:
        customers = Customer.objects.all()
    return render(request, 'agent/agent_list_customers.html', {'customers': customers})

# Agent Health Policy Application

@login_required
def agent_select_customer(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        if customer_id:
            try:
                # Ensure the customer exists in the database
                Customer.objects.get(id=customer_id)
                # Store the customer_id in the session
                request.session['customer_id'] = customer_id
                # Redirect to the next view
                return redirect('agent_health-plan-list')
            except Customer.DoesNotExist:
                # Handle the case where the customer ID does not exist
                messages.error(request, "Customer does not exist.")
                return redirect(request.path)  # Redirect back to the same page to reselect
        else:
            # Handle case where customer_id is not provided or empty
            messages.error(request, "Invalid customer selection.")
            return redirect(request.path)  # Redirect back to the same page to reselect

    # Handle non-POST methods such as GET, and guide the user or prevent this route's misuse
    messages.error(request, "This operation is not supported.")
    return redirect('some_default_route')  # Redirect to a default route, e.g., customer list

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import HealthPlan, HealthPolicy, Office, Agent, User
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

# List of health plans for agents
@login_required
def agent_health_plan_list(request):
    records = HealthPlan.objects.all().values_list('id', 'ptype', 'ypremium', 'incper', 'maxamt', 'specification', 'uptoage')
    if not records:
        records = None
    return render(request, 'agent/agent_health_policy_issue_00.html', {'records': records})

# First registration step by the agent
@login_required
def agent_register_healthpolicy(request, plan_id):
    plan = get_object_or_404(HealthPlan, pk=plan_id)
    offices = Office.objects.all()
    return render(request, 'agent/agent_health_policy_issue_01.html', {'plan': plan, 'offices': offices})

# Registration of number of members and office
@login_required
def agent_register_healthpolicy01(request, plan_id):
    plan = get_object_or_404(HealthPlan, pk=plan_id)
    offices = Office.objects.all()
    if request.method == 'POST':
        number_of_members = request.POST.get('number_of_members')
        office_id = request.POST.get('office_id')
        if number_of_members.isdigit() and int(number_of_members) > 0:
            request.session['number_of_members'] = number_of_members
            request.session['office_id'] = office_id
            return redirect('agent_register_healthpolicy02', plan_id=plan_id)
        else:
            messages.error(request, "Please enter a valid number of persons.")
    return render(request, 'agent/agent_health_policy_issue_01.html', {'plan': plan, 'offices': offices})

# Final confirmation and policy saving
@login_required
def agent_register_healthpolicy02(request, plan_id):
    agent = request.user.agents  # Get the agent associated with the current user
    customer_id = request.session.get('customer_id') 
    customer = Customer.objects.get(id=customer_id)
    plan = get_object_or_404(HealthPlan, pk=plan_id)
    number_of_members = int(request.session.get('number_of_members', 1))
    office_id = request.session.get('office_id')
    office = get_object_or_404(Office, pk=office_id)
    base_amount = plan.ypremium * number_of_members
    increment_amount = base_amount * (Decimal(plan.incper) / 100)
    total_amount = base_amount + increment_amount
    if total_amount > plan.maxamt:
        total_amount = plan.maxamt
    health_policy = HealthPolicy(
        customer=customer,
        agent=agent,
        health_plan=plan,
        npersons=number_of_members,
        amount=total_amount,
        appldate=date.today(),
        penddate=date.today() + timedelta(days=365),
        office=office,
        approval=True,
        appdate=date.today()
    )
    try:
        health_policy.save()
        messages.success(request, "Health policy registered successfully.")
        request.session['health_policy_id'] = health_policy.id
        return render(request, 'agent/agent_health_policy_issue_02.html', {'plan': plan, 'policy_id': health_policy.id, 'number_of_members': number_of_members})
    except Exception as e:
        logger.error(f"Failed to save health policy: {e}")
        messages.error(request, "Failed to save the policy due to an internal error.")
        return redirect('agent_register_healthpolicy', plan_id=plan_id)

# Submit member form data
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import traceback

@csrf_exempt
def agent_submit_member_form(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)

    try:
        name = request.POST.get('name')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        photo = request.FILES.get('photo')
        health_policy_id = request.session.get('health_policy_id')

        if not all([name, dob, gender, weight, height, photo]):
            return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

        weight = Decimal(weight)  # Ensure this conversion is safe
        height = Decimal(height)

        health_policy = HealthPolicy.objects.get(id=health_policy_id)
        member = HMembers(
            name=name,
            dob=dob,
            gender=gender,
            weight=weight,
            height=height,
            photo=photo,
            health_policy=health_policy
        )
        member.full_clean()  # Validate model instance
        member.save()
        return JsonResponse({"success": True, "message": "Member details saved successfully."})
    except Exception as e:
        logger.error("Error when saving member details: %s", str(e))
        logger.error(traceback.format_exc())  # Log the traceback to help with debugging
        return JsonResponse({"success": False, "message": "An error occurred during submission: " + str(e)}, status=500)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import HealthPlan, HealthPolicy, HMembers, Payment
from django.conf import settings
import razorpay
import logging

logger = logging.getLogger(__name__)

def agent_register_healthpolicy03(request, plan_id):
    plan = get_object_or_404(HealthPlan, pk=plan_id)
    health_policy_id = request.session.get('health_policy_id', None)

    if health_policy_id is None:
        return HttpResponseBadRequest("Health Policy ID not found in session")

    health_policy = get_object_or_404(HealthPolicy, pk=health_policy_id)
    members = HMembers.objects.filter(health_policy=health_policy)
    amount = int(health_policy.amount * 100)  # Convert to the smallest currency unit as required by Razorpay

    # Initialize Razorpay client
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    razorpay_order = razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": '0'
    })

    # Razorpay order ID to track this transaction
    razorpay_order_id = razorpay_order['id']
    callback_url = '/agent_paymenthandler1/'  # Assuming this is the endpoint where payment verification is handled

    context = {
        'plan': plan,
        'policy': health_policy,
        'members': members,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': 'INR',
        'callback_url': callback_url
    }
    return render(request, 'agent/agent_health_policy_issue_03.html', context)

@csrf_exempt
def agent_paymenthandler1(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    # Collect the details from the post request
    payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    signature = request.POST.get('razorpay_signature', '')
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    # Verify the payment signature
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    try:
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if not result:
            logger.error("Signature verification failed")
            return render(request, 'payment_fail.html')

        health_policy_id = request.session.get('health_policy_id')
        if not health_policy_id:
            logger.error("Health policy ID not found in session")
            return HttpResponseBadRequest("Health Policy ID not found in session")

        health_policy = HealthPolicy.objects.get(id=health_policy_id)

        # Log the successful payment
        payment = Payment(
            health_policy=health_policy,
            amount=health_policy.amount,
            payment_date=timezone.now(),
            razorpay_order_id=razorpay_order_id
        )
        payment.save()

        return render(request, 'agent/agent_health_premium_payment.html', {'health_policy': health_policy})
    except HealthPolicy.DoesNotExist:
        logger.error("Health Policy not found with ID from session")
        return HttpResponseBadRequest("Health Policy not found")
    except Exception as e:
        logger.error(f"Error processing the payment: {e}")
        return HttpResponseBadRequest(f"Error in processing your payment: {e}")
    



    # Agent Vehicle Policy Application


@login_required
def agent_select_customer_vehicle(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        if customer_id:
            try:
                Customer.objects.get(id=customer_id)
                request.session['customer_id'] = customer_id
                # Redirect to the vehicle policy plan list or a specific vehicle policy application view
                return redirect('agent_register_vehicle_policy')
            except Customer.DoesNotExist:
                messages.error(request, "Customer does not exist.")
                return HttpResponseBadRequest("Customer does not exist.")
        else:
            messages.error(request, "Invalid customer selection.")
            return HttpResponseBadRequest("Invalid customer selection.")

    # Handle non-POST methods such as GET
    messages.error(request, "This operation is not supported.")
    return redirect('agent_list_customers')  # Redirect to a default route, e.g., customer list


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User, Customer, Office, VehiclePlan, VehiclePolicy
from decimal import Decimal
import datetime
import logging

logger = logging.getLogger(__name__)

@login_required
def agent_register_vehicle_policy(request):
    current_year = datetime.datetime.now().year
    years = range(1990, current_year + 1)
    user = request.user
    customer = getattr(user, 'customer', None)
    
    if not customer:
        logger.error(f"No customer associated with user {user.id}")
        return HttpResponse("No customer profile available.", status=400)

    offices = Office.objects.all()
    plans = VehiclePlan.objects.all()

    context = {
        'customer': customer,
        'offices': offices,
        'plans': plans,
        'years': years,
    }

    if request.method == 'POST':
        vehno = request.POST.get('t2', '').strip()
        vehvalue = Decimal(request.POST.get('t3', 0))
        vpid = request.POST.get('t4')
        enginno = request.POST.get('t5')
        chno = request.POST.get('t6')
        vehsize = request.POST.get('t7')
        vehcompany = request.POST.get('t8')
        vehpower = request.POST.get('t9')
        mfyear = int(request.POST.get('t10'))
        vehtype = request.POST.get('t11')
        officeid = request.POST.get('t12')
        vehphoto = request.FILES.get('file')

        try:
            plan = VehiclePlan.objects.get(id=vpid)
            office = Office.objects.get(officeid=officeid)

            policy_amount = calculate_policy_amount(vehvalue, plan)
            
            policy = VehiclePolicy(
                customer=customer,
                vehicle_number=vehno,
                vehicle_value=vehvalue,
                vehicle_plan=plan,
                engine_number=enginno,
                chassis_number=chno,
                vehicle_size=vehsize,
                vehicle_company=vehcompany,
                vehicle_power=vehpower,
                manufacture_year=mfyear,
                office=office,
                vehicle_photo=vehphoto,
                vehicle_type=vehtype,
                policy_amount=policy_amount,
                policy_date=datetime.date.today(),
                policy_end_date=datetime.date.today() + datetime.timedelta(days=365)
            )
            policy.save()
            logger.info(f"Vehicle Policy for {vehno} created successfully.")
            return redirect('policy_success')
        except (VehiclePlan.DoesNotExist, Office.DoesNotExist, ValueError) as e:
            logger.error(f"Error processing your request: {e}")
            return HttpResponse(f"Error processing your request: {e}", status=400)
    else:
        return render(request, 'customer/customer_vehicle_policyissue.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import VehiclePolicy
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
 
 
# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import VehiclePolicy
import qrcode
from io import BytesIO
from base64 import b64encode

@login_required
def policy_success(request):
    customer = request.user.customer
    vehicle_policy = VehiclePolicy.objects.filter(customer=customer).order_by('-policy_date', '-id').first()
    if not vehicle_policy:
        return render(request, 'error.html', {'message': 'No vehicle policy found for this customer.'})
    
    # Generate QR code for the vehicle policy
    qr_data = f"User: {customer.user.get_full_name()}\nPolicy Number: {vehicle_policy.id}\nVehicle Number: {vehicle_policy.vehicle_number}\nPolicy Amount: {vehicle_policy.policy_amount}\nPolicy End Date: {vehicle_policy.policy_end_date}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_base64 = b64encode(img_buffer.getvalue()).decode('utf-8')

    context = {
        'customer': customer,
        'vehicle_policy': vehicle_policy,
        'qr_code': img_base64,
    }
    return render(request, 'customer/customer_vehicle_premium_payment.html', context)



def calculate_policy_amount(vehvalue, plan):
    depreciation_factor = Decimal(plan.depreciation / 100)
    plan_percentage = Decimal(plan.Ppercentage / 100)  # Changed from 'percentage' to 'Ppercentage'
    return (vehvalue - (vehvalue * depreciation_factor)) * (1 + plan_percentage)

def customer_vehicle_premium_payment(request):
    # Your payment processing logic here
    return render(request, 'customer/customer_vehicle_premium_payment.html')

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import VehiclePolicy, Payment
import logging
from django.utils import timezone

# Assuming razorpay_client is properly initialized and imported
logger = logging.getLogger(__name__)

@csrf_exempt
def paymenthandler(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")
    

    payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    signature = request.POST.get('razorpay_signature', '')
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        # Verify the payment signature
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if not result:
            logger.error("Signature verification failed")
            return render(request, 'paymentfail.html')

        # Retrieve vehicle policy using session
        vehicle_policy_id = request.session.get('vehicle_policy_id')
        if not vehicle_policy_id:
            logger.error("Vehicle policy ID not found in session")
            return HttpResponseBadRequest("Vehicle Policy ID not found in session")

        vehicle_policy = VehiclePolicy.objects.get(id=vehicle_policy_id)

        # Create and save the payment object
        payment = Payment(
            vehicle_policy=vehicle_policy,
            amount=vehicle_policy.policy_amount,
            payment_date=timezone.now(),
            razorpay_order_id=razorpay_order_id
        )
        payment.save()

        return render(request, 'customer/customer_vehicle_premium_payment.html')

    except VehiclePolicy.DoesNotExist:
        logger.error("Vehicle Policy not found with ID from session")
        return HttpResponseBadRequest("Vehicle Policy not found")
    except KeyError as e:
        logger.error(f"Missing key in POST data or session: {e}")
        return HttpResponseBadRequest(f"Bad request: Missing data {e}")
    except Exception as e:
        logger.error(f"Error processing the payment: {e}")
        return HttpResponseBadRequest(f"Error in processing your payment: {e}")

from .models import VehiclePolicy
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import qrcode
from io import BytesIO

@login_required
def generate_policy_qr(request):
    # Retrieve Customer instance directly from User
    try:
        customer = request.user.customer
    except AttributeError:
        return HttpResponse("No customer profile associated with this user.", status=404)

    # Get the last vehicle policy for this customer
    vehicle_policy = VehiclePolicy.objects.filter(customer=customer).order_by('-policy_date').first()
    
    if not vehicle_policy:
        return HttpResponse("No vehicle policy found for this customer.", status=404)

    # Fetch user's full name from the Customer model
    user_name = f"{customer.first_name} {customer.last_name}".strip()

    # Generate QR code data with user's name and policy details
    qr_data = f"User: {user_name}\nPolicy Number: {vehicle_policy.id}\nVehicle Number: {vehicle_policy.vehicle_number}\nVehicle Value: {vehicle_policy.vehicle_value}\nPolicy Amount: {vehicle_policy.policy_amount}\nPolicy End Date: {vehicle_policy.policy_end_date}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Save image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    # Return the image as a response
    return HttpResponse(buffer, content_type="image/png")


