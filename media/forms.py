from django import forms
from .models import Image, Video

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = '__all__'
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': False}),
        }

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = '__all__'
        widgets = {
            'video': forms.ClearableFileInput(attrs={'multiple': False}),
        }

class MediaForm(forms.Form):
    MEDIA_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    media_type = forms.ChoiceField(choices=MEDIA_CHOICES, widget=forms.RadioSelect)
    media = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': False}))