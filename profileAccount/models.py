import os

from PIL import Image
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User


def image_location(instance, filename):
    file_path = 'profile/user_{username}/profile.jpeg'.format(
        username=str(instance.id), filename=filename,
    )
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    return file_path


# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, name, password):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")
        if not name:
            raise ValueError("Users must have their name")
        if not password:
            raise ValueError("Must secure account with password")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
            name=name,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100, unique=False)
    image_profile = models.ImageField(upload_to=image_location, default="user.png",
                                      null=True, blank=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    login_status = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    objects = MyAccountManager()

    def get_absolute_url(self):
        return reverse('profile', args=[self.username])

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


@receiver(post_save, sender=Account)
def save_profile_img(sender, instance, *args, **kwargs):
    SIZE = 600, 600
    if instance.image_profile:
        pic = Image.open(instance.image_profile.path)
        if pic.mode in ("RGBA", 'P'):
            pic = pic.convert("RGB")
            pic.thumbnail(SIZE, Image.LANCZOS)
            pic.save(instance.image_profile.path)


class Follower(models.Model):
    follower = models.CharField(max_length=1000)
    user = models.CharField(max_length=1000)

    def __str__(self):
        return self.user

