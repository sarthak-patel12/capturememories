from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
	email = models.EmailField(unique = True)
	phone_number = models.TextField(unique = True)
	is_verified = models.BooleanField(default = False)
	is_subuser = models.BooleanField(default = False)
	parent_user_group_name = models.TextField(default = "Null",null = True)
	user_group = models.TextField(default= "Null",null = True)
	admin_authenticated = models.BooleanField(default=False)

class Email_Timer(models.Model):
	email = models.EmailField(unique = True,primary_key=True)
	time = models.DateTimeField(auto_now=True)
	counter = models.IntegerField()
	def __str__(self):
		return self.email

class Verification_code(models.Model):
	email = models.EmailField(unique = True,primary_key=True)
	code = models.IntegerField()
	def __str__(self):
		return self.email