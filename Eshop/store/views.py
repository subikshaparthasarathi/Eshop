from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode

from Eshop.tokens import generate_token
from .models import Product
from .models import Category
from .models import Customer
from django.contrib.auth.hashers import make_password, check_password
from Eshop import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def index(request):
    products = None
    categories = Category.get_all_categories()
    category_id = request.GET.get('category')
    if category_id:
        products = Product.get_all_products_by_category_id(category_id)
    else:
        products = Product.get_all_products()

    data = {}
    data['products'] = products
    data['categories'] = categories
    return render(request, 'index.html', data)


def validatecustomer(customer):
    error_message = None
    if not customer.first_name:
        error_message = 'First name Required !!'
    elif len(customer.first_name) < 4:
        error_message = 'First name must be 4 char long !!'
    elif not customer.last_name:
        error_message = 'Last name required'
    elif len(customer.last_name) < 4:
        error_message = 'Last name must be 4 char long !!'
    elif not customer.phone:
        error_message = 'phone number required'
    elif len(customer.phone) < 10:
        error_message = 'phone number must be 10 char long'
    elif len(customer.password) < 6:
        error_message = 'password must be 6 char long'
    elif len(customer.email) < 5:
        error_message = 'email must be 5 char long'
    elif customer.isExists():
        error_message = 'Email Address Already Registered'
    return error_message



def registeruser(request):
    first_name = request.POST.get('Firstname')
    last_name = request.POST.get('Lastname')
    phone = request.POST.get('Phonenumber')
    email = request.POST.get('email')
    password = request.POST.get('password')

    value = {'first_name': first_name, 'last_name': last_name, 'phone': phone, 'email': email}
    error_message = None
    customer = Customer(first_name=first_name, last_name=last_name, email=email, password=password, phone=phone)
    error_message = validatecustomer(customer)

    #saving



    if not error_message:

        customer.password = make_password(customer.password)
        customer.is_active=False
        customer.register()
        print(customer.first_name, customer.last_name, customer.phone, email, password)

        # welcome email

        subject = "welcome to AZ-Django login!!"
        message = "Hello " + customer.first_name + "!!\n" + "welcome to AZ!!" + "\n" + "Thank you for visiting our website" + "\n" + "We have also sent you a confirmation mail" + "please confirm your email address in order to activate your account" + "Thanking you!"

        from_email = settings.EMAIL_HOST_USER
        to_list = [customer.email]
        send_mail(subject, message, from_email, to_list, fail_silently = True)

        # Email address confirmation mail

        current_site = get_current_site(request)
        email_subject = "confirm your mail @ AZ django login!!"
        message2 = render_to_string('email_confirmation.html', {
            'name': customer.first_name, 
            'domain': current_site.domain, 
            'uid': urlsafe_base64_encode(force_bytes(customer.pk)), 
            'token': generate_token.make_token(customer)
        })
        
        email = EmailMessage(
            email_subject, 
            message2, 
            settings.EMAIL_HOST_USER, [customer.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('homepage')
    else:
        data = {'error': error_message, 'values': value}
        return render(request, 'signup.html', data)




def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    else:
        return registeruser(request)



def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        print(customer)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                return redirect('homepage')
            else:
                error_message = 'Email or password invalid !!'
        else:
            error_message = 'Email or password invalid !!'

        print(email, password)
        return render(request, 'login.html', {'error': error_message})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_encode(uidb64))
        customer = Customer.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Customer.DoesNotExist):
        customer = None

    if customer is not None and generate_token.check_token(customer, token):
        customer.is_active = True 
        customer.save()
        return render(request, 'login.html')
        #return redirect('homepage')
    else:
        return render(request, 'activation_failed.html')

















# Create your views here.
