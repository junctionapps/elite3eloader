from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Custom user based on Django best practices
    https://docs.djangoproject.com/en/2.1/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
    """

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)


class UserProfile(models.Model):
    """ Holds profile details for this user """
    pass


class License(models.Model):
    """ Holds the date the license was agreed to """
    agreed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agreed}"
