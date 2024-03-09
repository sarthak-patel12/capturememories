from django.contrib import admin
from .models import User, Email_Timer, Verification_code
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,  # original form fieldsets, expanded
        (                      # new fieldset added on to the bottom
            'None',  # group heading of your choice; set to None for a blank space instead of a header
            {
                'fields': (
                    'phone_number',
					'is_verified',
					'is_subuser',
					'parent_user_group_name',
					'user_group',
					'admin_authenticated'
                ),
            },
        ),
    )

admin.site.register(User,CustomUserAdmin)
admin.site.register(Email_Timer)
admin.site.register(Verification_code)
