from . models import CustomUser
from django.contrib.auth.backends import BaseBackend


# custom backend to allow login with both username or email
class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        if email:
            kwargs['email'] = email
        elif username:
            kwargs['username'] = username
        else:
            print("here in else")
            return None
        
        try:
            user = CustomUser.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None