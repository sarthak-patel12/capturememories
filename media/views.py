from django.shortcuts import render,redirect,get_object_or_404
from users.models import User, Email_Timer, Verification_code
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from home.views import home
from django.conf import settings
from email.message import EmailMessage
import smtplib
from smtplib import *
from .forms import MediaForm
from .models import Image,Video
import os
from django.contrib.auth.decorators import login_required
import time

# Create your views here.
from random import randint

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def register_eventuser(request):
	if request.method == "POST":
		context={'data':request.POST,'sent_code':False}
		user_name = request.POST.get('email')
		first_name = request.POST.get('fname')
		last_name = request.POST.get('lname')
		email = user_name
		phone_number = request.POST.get('phone_number')
		password = request.POST.get('password')
		user_group = request.POST.get('event_code')
		print()
		user_obj1 = User.objects.filter(phone_number = phone_number)
		user_obj = User.objects.filter(username = user_name)
		user_obj_parent = User.objects.filter(user_group=user_group)
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
		if not user_group:
			messages.add_message(request, messages.WARNING, "Please Enter Event Code.")
			Flag = True
		if Flag:
			return render(request,"register_eventuser.html",context)
		if user_obj:
			messages.add_message(request, messages.WARNING, "Email already registered.")
			return render(request,"register_eventuser.html",context)
		if user_obj1:
			messages.add_message(request, messages.WARNING, "Phone Number already registered.")
			return render(request,"register_eventuser.html",context)
		if not user_obj_parent:
			messages.add_message(request,messages.WARNING, "Wrong Event Code.")
			return render(request,"register_eventuser.html",context)
		
		get_v_code = Verification_code.objects.filter(email=email)
		print(settings.VERIFICATION_CODE)
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
					return render(request,"register_eventuser.html",context)
			v_code_object = Verification_code()
			v_code_object.email = email		
			try:
				v_code_object.code = send_verification_email(email=email)
				v_code_object.save()
				messages.add_message(request, messages.INFO, "Verification code sent to given Email.")
				context['sent_code'] = True
				context['resend_password'] = True
			except:
				print("exception raised")
				messages.add_message(request, messages.INFO, "Unable to send verification_code please check your email or try after sometime.")
			#user = User(first_name=first_name,last_name=last_name,username=user_name,email=email,phone_number=phone_number)
			#user.set_password(password)
			#user.save(commit=False)
			return render(request,"register_eventuser.html",context)
		
		if request.POST.get('v_code'):
			v_code = request.POST.get('v_code')
			get_v_code = get_object_or_404(Verification_code,pk=email)
			print(v_code)
			print(get_v_code.code)
			if int(v_code) == get_v_code.code:
				print("in verification")
				#settings.VERIFICATION_CODE = '000000'
				user = User(first_name=first_name,last_name=last_name,username=user_name,email=email,phone_number=phone_number,user_group=user_group)
				user.set_password(password)
				user.is_verified = True
				user.admin_authenticated = True
				user.is_subuser = True
				#user.group = email.split("@")[0]
				user.parent_user_group_name = user_group
				user.save()
				get_v_code.delete()
				get_timer = Email_Timer.objects.filter(email=email)
				get_timer.delete()
			else:
				context['sent_code'] = True
				context['resend_password'] = True
				messages.add_message(request, messages.INFO, "Wrong Verification code.Please try again")
				return render(request,"register_eventuser.html",context)
		
		
			messages.add_message(request, messages.INFO, "User Registered")
			return render(request,"login_eventuser.html")
		context['sent_code'] = True
		context['resend_password'] = True
		messages.add_message(request, messages.INFO, "Email already sent to registered email id. Please retry if not found.")
		return render(request,"register_eventuser.html",context)
		#return render(request,'verify_email',{'email':email})

	return render(request,'register_eventuser.html')

def resend_otp_s(request):
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
				return render(request,"register_eventuser.html",context)
		get_v_code = get_object_or_404(Verification_code,pk=email)
		get_v_code.code = send_verification_email(email=email)
		get_v_code.save()
		messages.add_message(request, messages.INFO, f"Verification code sent to {email} again. Count = {get_timer.counter}")
		context['sent_code'] = True
		context['resend_password'] = True
		
	return render(request,"register_eventuser.html",context)

def send_verification_email(email):
	try:
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
	except SMTPResponseException as e:
		error_code = SMTPResponseException.smtp_code
		error_message = SMTPResponseException.smtp_error
		print ("Error code:"+ error_code)
		print ("Message:"+ error_message)
		if (error_code==422):
			print ("Recipient Mailbox Full")
		elif(error_code==431):
			print ("Server out of space")
		elif(error_code==447):
			print ("Timeout. Try reducing number of recipients")
		elif(error_code==510 or error_code==511):
			print ("One of the addresses in your TO, CC or BBC line doesn't exist. Check again your recipients' accounts and correct any possible misspelling.")
		elif(error_code==512):
			print ("Check again all your recipients' addresses: there will likely be an error in a domain name (like mail@domain.coom instead of mail@domain.com)")
		elif(error_code==541 or error_code==554):
			print ("Your message has been detected and labeled as spam. You must ask the recipient to whitelist you")
		elif(error_code==550):
			print ("Though it can be returned also by the recipient's firewall (or when the incoming server is down), the great majority of errors 550 simply tell that the recipient email address doesn't exist. You should contact the recipient otherwise and get the right address.")
		elif(error_code==553):
			print ("Check all the addresses in the TO, CC and BCC field. There should be an error or a misspelling somewhere.")
		else:
			print (error_code+": "+error_message)
		return '0'
	return verification_code	

def login_eventuser(request):
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
		print("in subuser login")
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
			return render(request,"login_eventuser.html")

		if user_obj[0].is_subuser:
			messages.add_message(request,messages.WARNING,"Welcome to the event")
			#return render(request,"login_eventuser.html")

		user = authenticate(request,username=username,password=password)
		if not user:
			messages.add_message(request,messages.ERROR,"Invalid Credentials")
			return render(request,"login_eventuser.html")
		
		login(request,user)
		messages.add_message(request,messages.SUCCESS,"Login Success")
		return redirect('subuser_home')

	return render(request,'login_eventuser.html')


def subuser_home(request):

	return render(request,'subuser_home.html')

@login_required(login_url='index')
def upload_media(request, *args, **kwargs):
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        user_obj=request.user
        if form.is_valid():
            media_type = form.cleaned_data.get('media_type')
            files = request.FILES.getlist('media')
            for file in files:
                if media_type == 'image':
                    Image.objects.create(image=file,subuser=user_obj,user_group=user_obj.user_group)
                elif media_type == 'video':
                    Video.objects.create(video=file,subuser=user_obj,user_group=user_obj.user_group)

            return render(request, 'upload_successfull.html', {'media_type': media_type})
    else:
        form = MediaForm()

    return render(request, 'upload_media.html', {'form': form})
@login_required(login_url='index')
def delete_media(request,media_id):
	user = request.user
	try:
		media = get_object_or_404(Image,pk=media_id)   
	except:
		media = get_object_or_404(Video,pk=media_id)


	media_type = None

	if request.method == 'POST':
		if isinstance(media, Image):
			media_type = 'image'
			os.remove(media.image.path)
		elif isinstance(media, Video):
			media_type = 'video'
			os.remove(media.video.path)
		media.delete()
	images = Image.objects.filter(user_group=user.user_group)
	videos = Video.objects.filter(user_group=user.user_group)
	if user.is_superuser:
		images = Image.objects.all()
		videos = Video.objects.all()
	return render(request, 'view_media.html', {'images': images, 'videos': videos})
	#messages.success(request, f"{media_type.capitalize()} has been deleted successfully.")
	return HttpResponseRedirect('view_media')
@login_required(login_url='index')
def view_media(request,*args, **kwargs):
	user = request.user
	images = Image.objects.filter(user_group=user.user_group)
	videos = Video.objects.filter(user_group=user.user_group)
	if user.is_superuser:
		images = Image.objects.all()
		videos = Video.objects.all()
	#print(user.user_group)
	return render(request, 'view_media.html', {'images': images, 'videos': videos})

def download(request,file_name):

  	file_path = settings.MEDIA_ROOT +'/'+ file_name
  	file_wrapper = FileWrapper(file(file_path,'rb'))
  	file_mimetype = mimetypes.guess_type(file_path)
  	response = HttpResponse(file_wrapper, content_type=file_mimetype )
  	response['X-Sendfile'] = file_path
  	response['Content-Length'] = os.stat(file_path).st_size
  	response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name) 

  	return response