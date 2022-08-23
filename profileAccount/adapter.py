from allauth.account.signals import user_signed_up
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.signals import pre_social_login
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from profileAccount.models import Account
from django.conf import settings


class SocialAdapter(DefaultSocialAccountAdapter):

        @receiver(user_signed_up)
        def retrieve_social_data(self, request, user, **kwargs):
            """Signal, that gets extra data from sociallogin and put it to profile."""
            # get the profile where i want to store the extra_data
            profile = Account(user=user)
            # in this signal I can retrieve the obj from SocialAccount
            data = SocialAccount.objects.filter(user=user, provider='google')
            # check if the user has signed up via social media
            if data:
                picture = data[0].get_avatar_url()
                if picture:
                    # custom def to save the pic in the profile
                    save_image_from_url(model=profile, url=picture)
                profile.save()


def pre_save_pre_social_login_receiver(sender, instance, sociallogin, *args, **kwargs):
    if not instance.image_profile:
        instance.image_profile = sociallogin.account.extra_data.get('picture', None)


pre_social_login.connect(pre_save_pre_social_login_receiver, sender=Account)
