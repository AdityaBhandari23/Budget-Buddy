#accoutn_activation_token AND token_generator both are same thing Crycetruly has used account_Activation_token and we have used token_generator in utils.py
 
from django.shortcuts import render,redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str,DjangoUnicodeDecodeError #force_text has been removed in django force_str used here ##both work same
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from .utils import token_generator
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator

import threading

# Create your views here.

class EmailThread(threading.Thread):
    
    def __init__(self,email):
        self.email=email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)    

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
                activateurl='http://' + domain + link
                email_subject="Activate Your Account"
                email_body='HI '+user.username+" Please use this link for verification\n" + activateurl
                email=EmailMessage(
                    email_subject,
                    email_body,
                    'adityagoapala5@gmail.com',
                    [email],
                )#check this template on django documentation
                EmailThread(email).start()
                # messages.success(request, "Account Successfully Created")
                    
            
        # messages.success(request,"success")   
        # messages.warning(request,"warning")   
        # messages.info(request,"info")   
        # messages.error(request,"error")   
        return render(request,'authentication/register.html')
    
class VerificationView(View):
    def get(self,request,uidb64,token):
        
        try:
            id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=id)
            print("User retrieved:", user) 
            
            # if not token_generator.token.check_token(user,token): 
            if not token_generator.check_token(user,token):   
                print("Invalid token")
                return redirect('login'+'?message='+'User already activated')
            
            if user.is_active:
                print("User is already active") 
                return redirect('login')
            user.is_active=True
            user.save()
            print("User is_active set to True")
            messages.success(request,'Account Activated')
            return redirect('login') 
        except Exception as ex:
            
            pass
        
        return redirect('login')    
        
    
    
        
class LoginView(View):
    def get(self,request):
        return render(request,'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' +
                                     user.username+' you are now logged in')
                    return redirect('expenses')
                messages.error(
                    request, 'Account is not active,please check your email')
                return render(request, 'authentication/login.html')
            messages.error(
                request, 'Invalid credentials,try again')
            return render(request, 'authentication/login.html')

        messages.error(
            request, 'Please fill all fields')
        return render(request, 'authentication/login.html')    
  
class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')   
    
class RequestPasswordReset(View):
    def get(self, request):
        return render(request,'authentication/reset-password.html')
    
    def post(self,request):
        email=request.POST['email'] #this email matches with template(html page) name of an email section
        context={
            "values":request.POST
        }
        if not validate_email(email):
            messages.error(request,"Please supply a valid email")
            return render(request,'authentication/reset-password.html',context)
        current_site=get_current_site(request)
        # user=request.objects.filter(email=email) #cryce truly
        user=User.objects.filter(email=email) #User has commented
        
        if user.exists():
            email_contents={
            'user':user[0],
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
            'token':PasswordResetTokenGenerator().make_token(user[0]),
            }
            
            link=reverse('reset-user-password',kwargs={
                'uidb64':email_contents['uid'],
                'token':email_contents['token']
            })    
            
            email_subject=" PASSWORD RESET INSTRUCTIONS "      
            reset_url ='http://'+current_site.domain+link
            
            email=EmailMessage(
                email_subject,
                'Hi there, Please click on the Link to reset your password \n'+reset_url,
                'noreply@semicolon.com',
                [email],
            )
            EmailThread(email).start()
        
        
        messages.success(request,'We have sent you an email..........')#when user is not registered
    
        return render(request,'authentication/reset-password.html')
    
class CompletePasswordReset(View):
    def get(self,request,uidb64,token):
        
        context={
            'uidb64':uidb64,
            'token': token
        }
        
        try:    
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.info(request,"Password Link is invalid. Please request a new one")
                return render(request,'authentication/reset-password.html')
        
        except Exception as identifier:
            pass
        
        
        return render(request,'authentication/set-new-password.html',context)
    
    
    
    
    def post(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token': token
        }  
        password=request.POST['password']
        password2=request.POST['password2']
        
        if password !=password2:
            messages.error(request,'Passwords Do Not Match')
            return render(request,'authentication/set-new-password.html',context)
        
        if len(password)<6:# these comments are irrevelant 
            messages.error(request,'Password Too Short')
            return render(request,'authentication/set-new-password.html',context) 
        try:    
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            
            messages.success(request,"Password Reset Successful. You can now login with new password")
            return redirect('login')
        
        except Exception as identifier:
            messages.info(
                request,'Something Went wrong, try again'
            )
            return render(request,'authentication/set-new-password.html',context)
        
        # return render(request,'authentication/set-new-password.html',context)    
    














