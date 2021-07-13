from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

USER_ROLES = (
    ('user', 'User role'),
    ('moderator', 'Moderator role'),
    ('admin', 'Admin role')
)

User = get_user_model()


# Расширяем модель User за счёт создания доп. модели
# Profile со связью one-to-one
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=50,
        choices=USER_ROLES,
        default=USER_ROLES[0],
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.username


# Установим сигнал для Profile на
# автоматическое создание, когда мы создаем
# стандартную модель пользователя User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# Установим сигнал для Profile на
# автоматическое обновление, когда мы обновляем
# стандартную модель пользователя User
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
