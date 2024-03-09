from django.db import models
from users.models import User
# Create your models here.

class Image(models.Model):
	subuser=models.ForeignKey(User,on_delete=models.CASCADE,related_name="image")
	image = models.ImageField(upload_to='images/')
	user_group = models.TextField(default= "Null",null = True)
	id = models.AutoField(primary_key=True)

	class Meta:
		ordering = ["subuser"]

class Video(models.Model):
	subuser=models.ForeignKey(User,on_delete=models.CASCADE, related_name="video")
	id = models.AutoField(primary_key=True)
	video = models.FileField(upload_to='videos/')
	user_group = models.TextField(default= "Null",null = True)
	class Meta:
		ordering = ["subuser"]
