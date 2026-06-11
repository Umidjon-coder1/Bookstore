from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from .forms import RegistrationForm, LoginForm, ProfileForm, ChangePasswordForm

User = get_user_model()


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('books:list')
        form = RegistrationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Ro\'yxatdan o\'tish muvaffaqiyatli! Iltimos, elektron pochtangizni tasdiqlang.')
            return redirect('books:list')
        return render(request, 'users/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('books:list')
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'books:list')
            messages.success(request, f'Xush kelibsiz, {user.get_full_name()}!')
            return redirect(next_url)
        return render(request, 'users/login.html', {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'Tizimdan chiqdingiz.')
        return redirect('books:list')

    def get(self, request):
        logout(request)
        return redirect('books:list')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = ProfileForm(instance=request.user)
        return render(request, 'users/profile.html', {'form': form})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
            return redirect('users:profile')
        return render(request, 'users/profile.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    def get(self, request):
        form = ChangePasswordForm()
        return render(request, 'users/password_change.html', {'form': form})

    def post(self, request):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['old_password']):
                form.add_error('old_password', 'Joriy parol noto\'g\'ri.')
                return render(request, 'users/password_change.html', {'form': form})
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Parol muvaffaqiyatli o\'zgartirildi!')
            return redirect('users:profile')
        return render(request, 'users/password_change.html', {'form': form})


def verify_email(request, token):
    user = get_object_or_404(User, email_verification_token=token)
    user.email_verified = True
    user.email_verification_token = ''
    user.save()
    messages.success(request, 'Elektron pochta muvaffaqiyatli tasdiqlandi!')
    return redirect('books:list')


def password_reset_request(request):
    from django.contrib.auth.forms import PasswordResetForm
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request, use_https=request.is_secure(),
                      email_template_name='users/password_reset_email.html')
            messages.success(request, 'Parolni tiklash xati yuborildi.')
            return redirect('users:login')
    else:
        form = PasswordResetForm()
    return render(request, 'users/password_reset.html', {'form': form})
