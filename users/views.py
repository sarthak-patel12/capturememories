from django.shortcuts import render,redirect,get_object_or_404
from .models import User, Email_Timer, Verification_code
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from home.views import home
from django.conf import settings
from email.message import EmailMessage
import smtplib
from random import randint
from media.models import Image,Video
from django.contrib.auth.decorators import login_required
import os
import time

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)
# Create your views here.

def register_user(request):
	if request.method == "POST":
		context={'data':request.POST,'sent_code':False}
		user_name = request.POST.get('email')
		first_name = request.POST.get('fname')
		last_name = request.POST.get('lname')
		email = user_name
		phone_number = request.POST.get('phone_number')
		password = request.POST.get('password')
		user_obj1 = User.objects.filter(phone_number = phone_number)
		user_obj = User.objects.filter(username = user_name)
		Flag = False
		if not first_name:
			messages.add_message(request, messages.WARNING, "Please Enter First Name.")
			Flag = True
		if not last_name:
			messages.add_message(request, messages.WARNING, "Please Enter Last Name.")
			Flag = True
		if not user_name:
			messages.add_message(request, messages.WARNING, "Please Enter Email.")
			Flag = True
		if not phone_number:
			messages.add_message(request, messages.WARNING, "Please Enter phone_number.")
			Flag = True
		if not password:
			messages.add_message(request, messages.WARNING, "Please Enter Password.")
			Flag = True
		if Flag:
			return render(request,"index.html",context)
		if user_obj:
			messages.add_message(request, messages.WARNING, "Email already registered.")
			return render(request,"index.html",context)
		if user_obj1:
			messages.add_message(request, messages.WARNING, "Phone Number already registered.")
			return render(request,"index.html",context)

		get_v_code = Verification_code.objects.filter(email=email)
		print (True if get_v_code else False)
		if not get_v_code:
			get_timer = Email_Timer.objects.filter(email=email)
			if not get_timer:
				timer = Email_Timer()
				timer.email = email
				timer.counter = 1
				#timer.time = time.time
				timer.save()
				print(timer.time)
			elif get_timer.counter<5:
				get_timer.counter = get_timer.counter+1
				get_timer.save()
			else:	
				last_sent_time = get_timer.time
				current_time = time.time()
				last_sent_time= time.mktime(last_sent_time.timetuple()) + last_sent_time.microsecond / 1E6
				time_difference = current_time-last_sent_time
				print(time_difference)
				if (time_difference/3600)>24:
					get_timer.counter = 1
					get_timer.save()
				else :
					messages.add_message(request, messages.ERROR, "Email attempts exausted. Please try after 24Hrs from last tried")
					return render(request,"index.html",context)

			v_code_object = Verification_code()
			v_code_object.email = email
			v_code_object.code = send_verification_email(email=email)
			v_code_object.save()
			messages.add_message(request, messages.INFO, "Verification code sent to given Email.")
			context['sent_code'] = True
			context['resend_password'] = True
			#user = User(first_name=first_name,last_name=last_name,username=user_name,email=email,phone_number=phone_number)
			#user.set_password(password)
			#user.save(commit=False)
			return render(request,"index.html",context)

		if request.POST.get('v_code'):
			get_v_code = get_object_or_404(Verification_code,pk=email)
			v_code = request.POST.get('v_code')
			temp = get_v_code.code
			print(type(temp))
			print(temp)
			print(type(v_code))
			if v_code == str(temp):				
				user = User(first_name=first_name,last_name=last_name,username=user_name,email=email,phone_number=phone_number)
				user.set_password(password)
				user.is_verified = True
				#user.admin_authenticated = True
				user.user_group = email.split("@")[0]
				user.save()
				get_v_code.delete()
				get_timer = Email_Timer.objects.filter(email=email)
				get_timer.delete()
			else:
				#settings.VERIFICATION_CODE = temp
				context['sent_code'] = True
				context['resend_password'] = True
				messages.add_message(request, messages.INFO, "Wrong Verification code.Please try again")
				return render(request,"index.html",context)

			
		
			messages.add_message(request, messages.INFO, "User Registered")
			return render(request,"login.html")

		context['sent_code'] = True
		context['resend_password'] = True
		#return render(request,'verify_email',{'email':email})
		messages.add_message(request, messages.INFO, "Email already sent to registered email id. Please retry if not found.")
		return render(request,'index.html',context)

	return render(request,'index.html')

def resend_otp(request):
	context = context={'data':request.POST,'sent_code':False}
	if request.method=="POST":
		email = request.POST.get('email')
		get_timer = get_object_or_404(Email_Timer,pk=email)
		t = get_timer.counter
		print(t+1)
		if get_timer.counter<5:
			get_timer.counter=t + 1
			print(get_timer.counter)
			get_timer.save()
			print(get_timer.counter)
		else:	
			last_sent_time = get_timer.time
			print(last_sent_time)
			last_sent_time= time.mktime(last_sent_time.timetuple()) + last_sent_time.microsecond / 1E6
			current_time = time.time()
			print(last_sent_time)
			print(current_time)
			time_difference = current_time-last_sent_time
			if (time_difference/3600)>24:
				get_timer.counter = 1
				get_timer.save()
			else :
				messages.add_message(request, messages.ERROR, "Email attempts exausted. Please try after 24Hrs from last tried")
				return render(request,"index.html",context)
		get_v_code = get_object_or_404(Verification_code,pk=email)
		get_v_code.code = send_verification_email(email=email)
		get_v_code.save()
		messages.add_message(request, messages.INFO, f"Verification code sent to {email} again. Count = {get_timer.counter}")
		context['sent_code'] = True
		context['resend_password'] = True
		
	return render(request,"index.html",context)


def send_verification_email(email):
	verification_code = random_with_N_digits(6)
	msg = EmailMessage()
	msg['Subject'] = 'Activate your account'
	msg['From'] = 'info.significativo@gmail.com'
	msg['To'] = [email]
	#print(phone_number)
	msg.set_content(f"""The verification code is {verification_code}""")
	with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
		smtp.login('info.significativo@gmail.com', 'tophsmfgejwaoqij')
		smtp.send_message(msg)
	return str(verification_code)	


def login_user(request):
	user = request.user
	if user.is_authenticated:
		if not user.is_subuser:
			return redirect('user_home')
		else:
			return redirect('subuser_home')
	if request.method == "POST":
		username = request.POST.get('email')
		password = request.POST.get('password')
		user_obj = User.objects.filter(username = username)
		Flag = False
		if not username:
			messages.add_message(request, messages.WARNING, "Please Enter Email.")
			Flag = True

		if not password:
			messages.add_message(request, messages.WARNING, "Please Enter Password.")
			Flag = True

		if not user_obj:
			messages.add_message(request, messages.WARNING, "Please Enter Correct Email or register before login.")
			Flag = True

		if Flag:
			return render(request,"login.html")

		if user_obj[0].is_subuser:
			messages.add_message(request,messages.WARNING,"This is the event organizer login. Please login from the event user link. You can get it from you event organizer or ongoing events in home page.")
			return render(request,"login.html")

		user = authenticate(request,username=username,password=password)
		if not user:
			messages.add_message(request,messages.ERROR,"Invalid Credentials")
			return render(request,"login.html")
		
		login(request,user)
		#messages.add_message(request,messages.SUCCESS,"Login Success")
		
		return redirect('user_home')

	return render(request,'login.html')

@login_required(login_url='index')
def logout_user(request):
	logout(request)
	messages.add_message(request,messages.SUCCESS,f'Successfully logged out')
	return render(request,'index.html')

@login_required(login_url='index')
def user_home(request):
	current_user = request.user
	print(current_user.user_group)
	data = User.objects.filter(parent_user_group_name=current_user.user_group)
	if current_user.is_superuser:
		data = User.objects.filter(is_staff = False)
		print(data)
	context = {
		'data':data
		}
	print(context)
	return render(request,'user_home.html',context)

@login_required(login_url='index')
def delete_user(request,user_id,flag):
	print(user_id)
	flag1 = False
	data= get_object_or_404(User,pk=user_id)
	user = request.user
	#messages.add_message(request,messages.SUCCESS,f'calling user_delet successfull')
	
	if not data.is_subuser:
		images = Image.objects.filter(user_group=data.user_group)
		videos = Video.objects.filter(user_group=data.user_group)
		flag1 = True
	else:
		images = Image.objects.filter(subuser=data)
		videos = Video.objects.filter(subuser=data)
	context={
		'data':data,
		'images': images, 
		'videos': videos,
		'flag': flag1
			}
	if flag=='yes':
		return render(request,'delete_user.html',context)
	if request.method == "POST":
		delete = request.POST.get('delete')
		print(delete)
		if delete == 'yes':
			restore_media = request.POST.get('restore_media')
			print(delete)
			print(restore_media)
			d_images = Image.objects.filter(subuser=data)
			d_videos = Video.objects.filter(subuser=data)
			if restore_media == None:
				for ima in d_images:
					os.remove(ima.image.path)
				for vi in d_videos:
					os.remove(ima.image.path)
				data.delete()
			if restore_media == 'yes':
				for ima in d_images:
					print(ima.subuser)
					ima.subuser = user
					print(ima.subuser)
					ima.save()
				for vi in d_videos:
					print(ima.subuser)
					vi.subuser = user
					print(vi.subuser)
					vi.save()
				data.delete()
			return redirect('user_home')
		else:
			return redirect('user_home')

	return render(request,'delete_user.html',context)
