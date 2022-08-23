import os
import urllib

from allauth.socialaccount.models import SocialAccount
from django.conf import settings

# Avoid shadowing the login() and logout() views below.
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordContextMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import resolve_url, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from my_test_reference import testingImage, create_or_get_path
from profileAccount.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from profileAccount.models import Account, Follower
from blogPost.models import BlogPost


# Create your views here.


def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            return redirect('home')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'account/register.html', context)


def logout_view(request):
    user = request.user
    acct = Account.objects.all().filter(username=user).first()
    acct.login_status = False
    acct.save()
    logout(request)
    return redirect('home')


def login_view(request):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect("home")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            acct = Account.objects.all().filter(username=user).first()
            acct.login_status = True
            acct.save()
            if user:
                login(request, user)
                return redirect("home")

    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    return render(request, 'account/login.html', context)


def account_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    context = {}

    if request.POST:
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.initial = {
                "email": request.POST['email'],
                "username": request.POST['username'],
                "name": request.POST['name'],
            }
        form.save()
        messages.success(request, "Your profile was updated successfully!")
    else:
        form = AccountUpdateForm(
            initial={
                "email": request.user.email,
                "username": request.user.username,
                "name": request.user.name,
                "image_profile": request.user.image_profile,
            }
        )
    context['account_form'] = form
    return render(request, 'account/account.html', context)


def profile_view(request, user):
    profile_id = get_object_or_404(Account, username=user)
    profile_obj = Account.objects.filter(username=profile_id)

    current_user = profile_obj.first()
    logged_in_user = request.user

    post_obj = BlogPost.objects.all().filter(author=profile_id)
    followers = Follower.objects.all().filter(user=profile_id)
    following = Follower.objects.all().filter(follower=profile_id)

    user_follow = Follower.objects.all().filter(user=profile_id)
    user_follow_list = []
    for i in user_follow:
        user_follow = i.follower
        user_follow_list.append(user_follow)
    if logged_in_user.username in user_follow_list:
        follower_value_button = 'unfollow'
    else:
        follower_value_button = 'follow'

    content = {
        'profile': profile_obj,
        'post': post_obj,
        'followers': followers,
        'following': following,
        'current_user': current_user,
        'logged_in_user': logged_in_user.username,
        'main_user': logged_in_user,
        'follower_value_button': follower_value_button,
    }
    return render(request, 'account/profile.html', content)


def follow_view(request, user):
    profile_id = get_object_or_404(Account, username=user)
    test = profile_id.get_absolute_url()

    if request.POST:
        value = request.POST['value']
        user = request.POST['user']
        follower = request.POST['follower']
        if value == 'follow':
            save_follow = Follower.objects.create(follower=follower, user=user)
            save_follow.save()
        else:
            remove_follow = Follower.objects.filter(follower=follower, user=user)
            remove_follow.delete()
    return redirect(test)


def profile_social_view(request):
    user_confirm = request.user.socialaccount_set.all().first()
    user_confirm1 = request.user.socialaccount_set.all()
    print(user_confirm1)
    account_confirm = SocialAccount.objects.all().filter(uid=user_confirm1[0].uid).first()
    social_account = request.user.socialaccount_set.all()

    image_profile = social_account[0].get_avatar_url()
    image_url = f"{image_profile}"

    profile_id = Account.objects.all().filter(username=user_confirm).first()
    path = f'media_cdn/profile/user_{profile_id.id}'
    create_or_get_path(path)

    filename = f'media_cdn/profile/user_{profile_id.id}/profile.jpeg'

    testingImage(image_url, filename)

    name = social_account[0].extra_data['name']
    profile_id.name = name
    profile_id.image_profile = f'/profile/user_{profile_id.id}/profile.jpeg'
    profile_id.save()

    content = {
        'profile': Account.objects.all().filter(username=user_confirm)
    }

    return render(request, 'account/profileView.html', content)


def delete_account(request):
    if request.POST:
        get_post = request.POST.get('get_post')

        if "ok" in get_post:
            posts.delete()
            return redirect('home')
        else:
            return redirect(test)

    return render(request, 'blogPost/snippets/delete_post.html')


def must_authenticate_view(request):
    return render(request, 'account/must_authenticate.html', {})


class PasswordResetView(PasswordContextMixin, FormView):
    email_template_name = "registration/password_reset_email.html"
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")
    template_name = "registration/password_reset_form.html"
    title = _("Password reset")
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)


INTERNAL_RESET_SESSION_TOKEN = "_password_reset_token"


class PasswordResetDoneView(PasswordContextMixin, TemplateView):
    template_name = "registration/password_reset_done.html"
    title = _("Password reset sent")


class PasswordResetConfirmView(PasswordContextMixin, FormView):
    form_class = SetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = "set-password"
    success_url = reverse_lazy("password_reset_complete")
    template_name = "registration/password_reset_confirm.html"
    title = _("Enter new password")
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (
                TypeError,
                ValueError,
                OverflowError,
                UserModel.DoesNotExist,
                ValidationError,
        ):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
        else:
            context.update(
                {
                    "form": None,
                    "title": _("Password reset unsuccessful"),
                    "validlink": False,
                }
            )
        return context


class PasswordResetCompleteView(PasswordContextMixin, TemplateView):
    template_name = "registration/password_reset_complete.html"
    title = _("Password reset complete")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = resolve_url(settings.LOGIN_URL)
        return context


class PasswordChangeView(PasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "registration/password_change_form.html"
    title = _("Password change")

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


class PasswordChangeDoneView(PasswordContextMixin, TemplateView):
    template_name = "registration/password_change_done.html"
    title = _("Password change successful")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
