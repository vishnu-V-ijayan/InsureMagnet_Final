from django.http import HttpResponse
from django.urls import path,include
from . import views

from django.contrib.auth.views import PasswordResetView,PasswordResetDoneView,PasswordResetConfirmView,PasswordResetCompleteView
urlpatterns = [
    path('', views.index,name="index"),
    path('signup/',views.Sign_up,name="signup"),
    path('handlelogin/',views.handlelogin,name="handlelogin"),
    path('handlelogout/',views.handlelogout,name="handlelogout"),
    path('activate/<uidb64>/<token>',views.ActivateAccountView.as_view(),name='activate'),
    path('customer_home/',views.customer_home,name="customer_home"),
    # path('view_policies/',views.view_policies,name="view_policies"),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    #path('admin_dashboard/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin_dashboard/',views.admin_dashboard_view,name="admin_dashboard"),
    #path('employee_signup/',views.employee_signup,name="employee_signup"),
    path('hospital_dashboard/',views.hospital_dashboard,name="hospital_dashboard"),

   

#############################################################################################

    path('admin-view-customer/', views.admin_view_customer_view, name='admin-view-customer'),
    path('update-customer/<int:pk>', views.update_customer_view,name='update-customer'),
    path('delete-customer/<int:pk>', views.delete_customer_view,name='delete-customer'),

    path('admin-category', views.admin_category_view,name='admin-category'),
    path('admin-view-category', views.admin_view_category_view,name='admin-view-category'),
    path('admin-update-category', views.admin_update_category_view,name='admin-update-category'),
    path('update-category/<int:pk>', views.update_category_view,name='update-category'),
    path('admin-add-category', views.admin_add_category_view,name='admin-add-category'),
    path('admin-delete-category', views.admin_delete_category_view,name='admin-delete-category'),
    path('delete-category/<int:pk>', views.delete_category_view,name='delete-category'),


    path('admin-policy', views.admin_policy_view,name='admin-policy'),
    path('admin-add-policy', views.admin_add_policy_view,name='admin-add-policy'),
    path('admin-view-policy', views.admin_view_policy_view,name='admin-view-policy'),
    path('admin-update-policy', views.admin_update_policy_view,name='admin-update-policy'),
    path('update-policy/<int:pk>', views.update_policy_view,name='update-policy'),
    path('admin-delete-policy', views.admin_delete_policy_view,name='admin-delete-policy'),
    path('delete-policy/<int:pk>', views.delete_policy_view,name='delete-policy'),

    path('admin-view-policy-holder', views.admin_view_policy_holder_view,name='admin-view-policy-holder'),
    path('admin-view-approved-policy-holder', views.admin_view_approved_policy_holder_view,name='admin-view-approved-policy-holder'),
    path('admin-view-disapproved-policy-holder', views.admin_view_disapproved_policy_holder_view,name='admin-view-disapproved-policy-holder'),
    path('admin-view-waiting-policy-holder', views.admin_view_waiting_policy_holder_view,name='admin-view-waiting-policy-holder'),
    path('approve-request/<int:pk>', views.approve_request_view,name='approve-request'),
    path('reject-request/<int:pk>', views.disapprove_request_view,name='reject-request'),

    path('admin-question', views.admin_question_view,name='admin-question'),
    path('update-question/<int:pk>', views.update_question_view,name='update-question'),


#Customer

    path('customer_dashboard', views.customer_dashboard,name='customer_dashboard'),

    path('customer/apply_policy_view/', views.apply_policy_view, name='apply_policy_view'),
    path('apply/<int:pk>', views.apply_view,name='apply'),
    path('history', views.history_view,name='history'),

    path('ask-question', views.ask_question_view,name='ask-question'),
    path('question-history', views.question_history_view,name='question-history'),
    path('customer/payment2/<int:item_id>/', views.payment2, name='payment2'),
    path('select_customer/', views.select_customer, name='select_customer'),
    path('customer_details/<int:customer_id>/', views.customer_details, name='customer_details'),


    path('staff-view-policy-holder', views.staff_view_policy_holder_view,name='staff-view-policy-holder'),
    path('staff-view-approved-policy-holder', views.staff_view_approved_policy_holder_view,name='staff-view-approved-policy-holder'),
    path('staff-view-disapproved-policy-holder', views.staff_view_disapproved_policy_holder_view,name='staff-view-disapproved-policy-holder'),
    path('staff-view-waiting-policy-holder', views.staff_view_waiting_policy_holder_view,name='staff-view-waiting-policy-holder'),
    path('staff-request/<int:pk>', views.staff_approve_request_view,name='staff-approve-request'),
    path('staff-request/<int:pk>', views.staff_disapprove_request_view,name='staff-reject-request'),

    # path('staff-question', views.staff_question_view,name='staff-question'),
    # path('staff-update-question/<int:pk>', views.staff_update_question_view,name='staff-update-question'),

    #path('register-office/', views.office_registration, name='register_office'),
    path('register/', views.register_staff, name='register'),
    path('satffhome/',views.staff_home,name="staffhome"),
    path('add-agent/', views.add_agent, name='add-agent'),
    path('agenthome/', views.agenthome, name='agenthome'),
    path('register_office', views.register_office, name='register_office'),
    path('office_success/<int:office_id>/', views.office_detail, name='office_success'),  # New URL for showing office details
    path('view_office/', views.view_office, name='view_office'),
    path('register-staff/', views.register_staff, name='register_staff'),
    path('admin-staff-registration-successful/', views.admin_staff_registration_successful, name='admin_staff_registration_successful'),
    path('list-offices/', views.list_offices, name='list_offices'),
    path('vehicle-plan-registration/', views.vehicle_plan_registration, name='vehicle_plan_registration'),
    path('healthplanreg2/', views.health_plan_registration, name='health_plan_registration'),
    #Admin adds Blog
    path('add/', views.add_blog_post, name='add_blog_post'),
    #customer watches blog
    path('blog_post_list/', views.blog_post_list, name='blog_post_list'),




# Guest users locates agents on map
    path('guest_map_agents/', views.view_agents, name='guest_map_agents'),

# health insurance cost prediction
 #path('healthinsurance_prediction/', views.healthinsurance_prediction, name='healthinsurance_prediction'),

# path('register/beneficiaries/', views.customer_health_policy_issue_02, name='customer_health_policy_issue_02'),
# path('register_healthpolicy01/',views.register_healthpolicy01,name='register_healthpolicy01'),
# path('register/', views.register_healthpolicy01, name='register_healthpolicy01'),
# path('customer_health_policy_issue_03/', views.customer_health_policy_issue_03, name='customer_health_policy_issue_03'),
    

# health insurance flow 00
    path('health-plans/', views.health_plan_list, name='health-plan-list'),
    path('health-plans/<int:plan_id>/', views.register_healthpolicy, name='register_healthpolicy'),
    path('health-plans/<int:plan_id>/register/', views.register_healthpolicy01, name='register_healthpolicy01'),
    path('health-plans/<int:plan_id>/register-members/', views.register_healthpolicy02, name='register_healthpolicy02'),
    path('submit/', views.submit_member_form, name='submit_member_form'),
    path('health-plans/<int:plan_id>/register-healthpolicy03/', views.register_healthpolicy03, name='register_healthpolicy03'),
    path('paymenthandler1/', views.paymenthandler1, name='paymenthandler1'),
    path('customer_health_premium_payment/', views.customer_health_premium_payment, name='customer_health_premium_payment'),

# health insurance claim management
    
    #path('health-policies/', views.view_health_policies, name='view-health-policies'),
    path('health_register_claim_00/', views.health_register_claim_00, name='health_register_claim_00'),
    path('health_register_claim_01/<int:policy_id>/', views.health_register_claim_01, name='health_register_claim_01'),
    path('health_register_claim_02/<int:policy_id>/', views.health_register_claim_02, name='health_register_claim_02'),
    path('health_register_claim_03/<int:policy_id>/', views.health_register_claim_03, name='health_register_claim_03'),

# Customer checks the policy status
    path('my-health-policies/', views.customer_health_policy_status_00, name='customer_health_policy_status_00'),
    path('my-vehicle-policy-status/', views.customer_vehicle_policy_status_00, name='customer_vehicle_policy_status_00'),

# Customer checks the claim status

    path('my-health-claim-status/', views.customer_health_claim_status_00, name='customer_health_claim_status_00'),
    path('my-vehicle-claim-status/', views.customer_vehicle_claim_status_00, name='customer_vehicle_claim_status_00'),





#customer end vehicle policy application
    path('register_policy/', views.register_vehicle_policy, name='register_policy'),
    path('policy_success/', views.policy_success, name='policy_success'),
    path('vehicle_premium_payment/', views.customer_vehicle_premium_payment, name='customer_vehicle_premium_payment'), 
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('policy/qr/',views.generate_policy_qr, name='policy-qr'),
    path('download_pdf/<int:policy_id>/', views.generate_policy_pdf, name='vehicle_generate_policy_pdf'),
    
 

 # vehicle insurance claim management
    
    path('vehicle_register-claim_00/', views.vehicle_register_claim_00, name='vehicle_register_claim_00'),
    path('vehicle_register_claim_01/<int:policy_id>/', views.vehicle_register_claim_01, name='vehicle_register_claim_01'),
    path('vehicle_register_claim_02/<int:policy_id>/', views.vehicle_register_claim_02, name='vehicle_register_claim_02'),
    path('vehicle_register_claim_03/<int:policy_id>/', views.vehicle_register_claim_03, name='vehicle_register_claim_03'),
    

#customer policy renew

path('vehicle-policies/', views.vehicle_policies_list, name='vehicle_policies_list'),
path('renew-policy/<int:policy_id>/', views.renew_policy, name='renew_policy'),
path('renew-health/', views.renew_health, name='renew_health'),
path('renew_policy_health0/<int:policy_id>/', views.renew_policy_health0, name='renew_policy_health0'),

  


# Agent is displayed on map

    path('agents-map/', views.agents_map, name='agents-map'),

# Staff Claim Approval

    path('claims/', views.ClaimListView.as_view(), name='staff_claim_list'),
    path('claims/verify/<int:claim_id>/', views.claim_verification, name='claim-verify'),
    path('vehicle-claim-approval/<int:claim_id>/', views.staff_vehicle_claim_approval_00, name='staff_vehicle_claim_approval_00'),
    path('health-claim-approval/<int:claim_id>/', views.staff_health_claim_approval_00, name='staff_health_claim_approval_00'),
    path('health_claims/approval/<int:claim_request_id>/',views.staff_health_claim_approval_01, name='staff_health_claim_approval_01'),
    path('vehicle_claims/approval/<int:claim_request_id>/',views.staff_vehicle_claim_approval_01, name='staff_vehicle_claim_approval_01'),

# Forgot Password

    path('request-reset-email/',views.RequestResetEmailView.as_view(),name="request-reset-email"),
    path("set-new-password/<uidb64>/<token>",views.SetNewPassword.as_view(),name="set-new-password"),

# Staff Policy Issue

    path('staff_list_customers/', views.staff_list_customers, name='staff_list_customers'),

    # Health Policy Handle

    path('staff_health-plans/<int:customer_id>/', views.staff_health_plan_list, name='staff_health_plan_list'),
    path('staff_register_healthpolicy/<int:plan_id>/', views.staff_register_healthpolicy, name='staff_register_healthpolicy'),
    path('staff_register_healthpolicy01/<int:plan_id>/', views.staff_register_healthpolicy01, name='staff_register_healthpolicy01'),
    path('staff_health-plans/<int:plan_id>/register-members/', views.staff_register_healthpolicy02, name='staff_register_healthpolicy02'),
    path('staff_submit/', views.staff_submit_member_form, name='staff_submit_member_form'),
    path('staff_health-plans/<int:plan_id>/register-healthpolicy03/', views.staff_register_healthpolicy03, name='staff_register_healthpolicy03'),
    path('paymenthandler02/', views.paymenthandler02, name='paymenthandler02'),

    # Vehicle Policy Handle
   
    path('staff_register_policy/<int:customer_id>/', views.staff_register_vehicle_policy, name='staff_register_policy'),
    # path('staff-register_policy/', views.staff-register_vehicle_policy, name='staff-register_policy'),
    path('staff-policy_success/', views.staff_policy_success, name='staff-policy_success'),
    path('staff-vehicle_premium_payment/', views.staff_vehicle_premium_payment, name='staff_vehicle_premium_payment'), 
    path('paymenthandler/', views.paymenthandler00, name='paymenthandler'),
    path('staff-policy/qr/',views.staff_generate_policy_qr, name='staff-policy-qr'),
    path('staff-download_pdf/<int:policy_id>/', views.staff_generate_policy_pdf, name='staff-vehicle_generate_policy_pdf'),

    # Agent policy issue handle

    path('agent_list_customers/', views.agent_list_customers, name='agent_list_customers'),


    # Health Policy Handle
    # health insurance flow 00
    path('agent_select-customer/', views.agent_select_customer, name='agent_select_customer'),
    path('agent_health-plans/', views.agent_health_plan_list, name='agent_health-plan-list'),
    path('agent_health-plans/<int:plan_id>/', views.agent_register_healthpolicy, name='agent_register_healthpolicy'),
    path('agent_health-plans/<int:plan_id>/register/', views.agent_register_healthpolicy01, name='agent_register_healthpolicy01'),
    path('agent_health-plans/<int:plan_id>/register-members/', views.agent_register_healthpolicy02, name='agent_register_healthpolicy02'),
    path('agent_submit/', views.agent_submit_member_form, name='agent_submit_member_form'),
    path('agent_health-plans/<int:plan_id>/register-healthpolicy03/', views.agent_register_healthpolicy03, name='agent_register_healthpolicy03'),
    path('agent_paymenthandler1/', views.agent_paymenthandler1, name='agent_paymenthandler1'),
    #path('agent_health_premium_payment/', views.agent_health_premium_payment, name='agent_health_premium_payment'),


]