from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings
from django.forms import ValidationError  # Use Django's setting for the AUTH_USER_MODEL

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.timezone import now

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        CUSTOMER = "CUSTOMER", 'Customer'
        STAFF = "STAFF", 'Staff'
        AGENT = "AGENT", 'Agent'
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=Role.choices)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, unique=True)
    aadhaar = models.CharField(max_length=12, unique=True)
    address = models.TextField()
    image = models.ImageField(upload_to="images/customer_images/", blank=True, null=True)
    place = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Category(models.Model):
    category_name =models.CharField(max_length=20)
    creation_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.category_name

class Policy(models.Model):
    category= models.ForeignKey('Category', on_delete=models.CASCADE)
    policy_name=models.CharField(max_length=200)
    sum_assurance=models.PositiveIntegerField()
    premium=models.PositiveIntegerField()
    tenure=models.PositiveIntegerField()
    creation_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.policy_name

class PolicyRecord(models.Model):
    customer= models.ForeignKey(Customer, on_delete=models.CASCADE)
    Policy= models.ForeignKey(Policy, on_delete=models.CASCADE)
    status = models.CharField(max_length=100,default='Pending')
    creation_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.status
    
class Question(models.Model):
    customer= models.ForeignKey(Customer, on_delete=models.CASCADE)
    description =models.CharField(max_length=500)
    admin_comment=models.CharField(max_length=200,default='Nothing')
    asked_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.description



class Office(models.Model):
    officeid = models.AutoField(primary_key=True)  # Changed to AutoField
    address = models.TextField()
    place = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    pin = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    regdate = models.DateField()

    def __str__(self):
        return self.place

class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User")
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, verbose_name="Office")
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=100, verbose_name="Address")
    place = models.CharField(max_length=100)
    pin = models.CharField(max_length=6)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
class Agent(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agents"
    )
    name = models.CharField(max_length=100)
    address = models.TextField()
    place = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    pin = models.CharField(max_length=6)
    phone = models.CharField(max_length=10)
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Male'), ('F', 'Female')]
    )
    qualification = models.CharField(max_length=100)
    aadhar = models.CharField(max_length=12, unique=True)
    photo = models.ImageField(upload_to='agent_photos/', blank=True, null=True)
    registration_date = models.DateField()
    staff = models.ForeignKey(
        'Staff', 
        on_delete=models.SET_NULL,
        null=True,
        related_name='agents'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"


class VehiclePlan(models.Model):
    PType = models.CharField(max_length=100, verbose_name='Premium Type')
    Ppercentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Premium Percentage')
    sp = models.TextField(verbose_name='Specifications and Conditions')
    depreciation = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.PType} - {self.Ppercentage}%"

from django.utils.translation import gettext_lazy as _

class VehiclePolicy(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name=_('Customer'))
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, verbose_name=_('Agent'), null=True, blank=True)
    vehicle_number = models.CharField(max_length=20, verbose_name=_('Vehicle Number'))
    vehicle_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Vehicle Value'))
    vehicle_plan = models.ForeignKey('VehiclePlan', on_delete=models.CASCADE, verbose_name=_('Vehicle Plan'))
    engine_number = models.CharField(max_length=50, verbose_name=_('Engine Number'))
    chassis_number = models.CharField(max_length=50, verbose_name=_('Chassis Number'))
    vehicle_size = models.CharField(max_length=50, verbose_name=_('Vehicle Size'))
    vehicle_company = models.CharField(max_length=100, verbose_name=_('Vehicle Company'))
    vehicle_power = models.CharField(max_length=50, verbose_name=_('Vehicle Power'))
    manufacture_year = models.IntegerField(verbose_name=_('Manufacture Year'))
    office = models.ForeignKey('Office', on_delete=models.CASCADE, verbose_name=_('Office'))
    vehicle_photo = models.ImageField(upload_to='vehicle_photos/', verbose_name=_('Vehicle Photo'))
    vehicle_type = models.CharField(max_length=50, verbose_name=_('Vehicle Type'))
    policy_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Policy Amount'))
    policy_date = models.DateField(verbose_name=_('Policy Date'))
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name=_('Staff'), null=True, blank=True)
    policy_end_date = models.DateField(verbose_name=_('Policy End Date'))

    def __str__(self):
        return f"VPID{self.id:04d}"  # Custom format e.g., VPID0001

class HealthPlan(models.Model):
    ptype = models.CharField(max_length=100)
    ypremium = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Yearly Premium")
    incper = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Coverage Increase Percentage")  # For percentages.
    maxamt = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Maximum Amount")
    specification = models.TextField()
    uptoage = models.IntegerField()

    # def display_health_plan_id(self):
    #     """Return the health plan ID with a custom format."""
    #     return f"HPID{self.id:04d}"  # Custom format e.g., HPID0001

    def __str__(self):
        return f"{self.ptype} ({self.id})"
    
class HealthPolicy(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name="Customer")
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, verbose_name=_('Agent'), null=True, blank=True)
    health_plan = models.ForeignKey('HealthPlan', on_delete=models.CASCADE, verbose_name="Health Plan")
    npersons = models.IntegerField(verbose_name="Number of Persons Covered")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Policy Amount")
    appldate = models.DateField(verbose_name="Application Date")
    office = models.ForeignKey('Office', on_delete=models.CASCADE, verbose_name="Office")
    penddate = models.DateField(verbose_name="Policy End Date")
    approval = models.BooleanField(verbose_name="Approval Status", default=True)
    appdate = models.DateField(verbose_name="Approval Date", default=now)
    comment = models.TextField(null=True, default=None)
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name=_('Staff'), null=True, blank=True)

    def __str__(self):
        return f"Policy #{self.id} for Customer {self.customer_id}"


from django.db import models
from datetime import date

class HMembers(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], db_column='sex')
    weight = models.DecimalField(max_digits=6, decimal_places=2)  # Assume weight in kilograms
    height = models.DecimalField(max_digits=5, decimal_places=2)  # Assume height in meters
    photo = models.ImageField(upload_to='member_photos/', blank=True, null=True)
    health_policy = models.ForeignKey('HealthPolicy', on_delete=models.CASCADE, related_name='members') 
    children = models.IntegerField(default=0)
    # region1 = models.IntegerField(choices=[(0, 'Northeast'), (1, 'Northwest'), (2, 'Southeast'), (3, 'Southwest')], null=True)
    # smoker = models.BooleanField(null=True)
  
class Payment(models.Model):
    # Django automatically provides an auto-incrementing primary key field named `id`, so you don't need to explicitly define `payno`.
    vehicle_policy = models.ForeignKey('VehiclePolicy', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Vehicle Policy'))
    health_policy = models.ForeignKey('HealthPolicy', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Health Policy'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Late Fee'))
    payment_date = models.DateField(verbose_name=_('Payment Date'))
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name=_('Staff'), blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Razorpay Order ID'))

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    def __str__(self):
        return f"{self.id} - {self.amount}"

class ClaimRequest(models.Model):
    # AutoField for an auto-incrementing primary key is implicit, can be omitted if 'id' is satisfactory
    vehicle_policy = models.ForeignKey('VehiclePolicy', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicle_claims')
    health_policy = models.ForeignKey('HealthPolicy', on_delete=models.SET_NULL, null=True, blank=True, related_name='health_claims')
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reports = models.TextField()
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=15)
    claim_date = models.DateField()

    def __str__(self):
        return f"{self.id} - {self.claim_amount}"

    class Meta:
        verbose_name = "Claim Request"
        verbose_name_plural = "Claim Requests"

from django.utils.translation import gettext_lazy as _

class BlogPost(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    heading = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)


    def __str__(self):
        return self.heading
    

class ClaimApproval(models.Model):
    claim_request = models.ForeignKey('ClaimRequest', on_delete=models.CASCADE, verbose_name=_('Request Number'), related_name='approvals')
    approval_status = models.CharField(max_length=50, verbose_name=_('Approval Status'))
    comment = models.TextField(verbose_name=_('Comment'))
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Approved Amount'), null=True, blank=True)
    approval_date = models.DateField(verbose_name=_('Approval Date'))
    staff = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='profile')

    class Meta:
        verbose_name = _('Claim Approval')
        verbose_name_plural = _('Claim Approvals')

    def __str__(self):
        return f"{self.claim_request.id} - {self.approval_status}"
