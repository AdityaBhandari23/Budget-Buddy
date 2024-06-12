from django.shortcuts import render,redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError #force_text has been removed
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from .utils import token_generator
# Create your views here.

class EmailvalidationView(View):
    def post(self,request):
        data=json.loads(request.body)
        email=data['email']
        
        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'},status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'email already taken,choose another one'},status=409)
        
        return JsonResponse({'email_valid':True})
        
class UsernamevalidationView(View):
    def post(self,request):
        data=json.loads(request.body)
        username=data['username']
        
        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only contain aphanumeric characters'},status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'username already taken,choose another one'},status=409)
        
        return JsonResponse({'username_valid':True})#here also we can add status code
        
class RegistrationView(View):
    def get(self,request):
        return render(request,'authentication/register.html') 
     
    def post(self,request):
        
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        
        context={
            'fieldValues':request.POST
        }
        
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request,'PASSWORD TOO SHORT IT SHOULD BE MINIMUM 6 CHARACTER LONG')
                    return render(request,'authentication/register.html',context)
            
                
                user=User.objects.create_user(username=username,email=email)
                user.set_password(password)
                user.is_active=False
                user.save()
                messages.success(request,"Account Succesfully Created")
                
                '''
                path to_view
                
                1. getting domain we are on
                2. relative url to verification
                3. encode uid
                4. token
                '''
                
                uidb64=urlsafe_base64_encode(force_bytes(user.pk))
                domain=get_current_site(request).domain
                link=reverse('activate',kwargs={
                    'uidb64':uidb64,
                    'token':token_generator.make_token(user),
                })
                activateurl='https://' + domain + link
                email_subject="Activate Your Account"
                email_body='HI'+user.username+"Please use this link for verification\n" + activateurl
                email=EmailMessage(
                    email_subject,
                    email_body,
                    'adityagoapala5@gmail.com',
                    [email],
                )#check this template on django documentation
                email.send(fail_silently=False)
                    
            
        # messages.success(request,"success")   
        # messages.warning(request,"warning")   
        # messages.info(request,"info")   
        # messages.error(request,"error")   
        return render(request,'authentication/register.html')
    
class VerificationView(View):
    def get(self,request,uidb64,token):
        return redirect('login')