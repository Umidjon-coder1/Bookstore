import secrets
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    if created and not instance.email_verified:
        token = secrets.token_urlsafe(32)
        User.objects.filter(pk=instance.pk).update(email_verification_token=token)
        verification_url = f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/users/verify-email/{token}/"
        try:
            send_mail(
                subject='Verify your email - Bookstore',
                message=f'Hi {instance.first_name or instance.email},\n\nPlease verify your email by clicking:\n{verification_url}\n\nThank you!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )
        except Exception:
            pass
