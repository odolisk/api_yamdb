from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

USER_ROLES = (
    ('user', 'User'),
    ('moderator', 'Moderator'),
    ('admin', 'Admin')
)


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer.',
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )
    first_name = models.CharField('first name', max_length=150, blank=True)
    last_name = models.CharField('last name', max_length=150, blank=True)
    email = models.EmailField(
        'email address',
        unique=True,
        help_text='Email address. Must be unique',
        error_messages={
            'unique': 'A user with that email already exists.',
        },)
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text='About me')
    role = models.CharField(
        max_length=50,
        choices=USER_ROLES,
        default=USER_ROLES[0],
        help_text='User role')
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Can use app or none')
    is_staff = models.BooleanField(
        'staff',
        default=False,
        help_text='Allow to login in django admin')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        return self.first_name


class Category(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f'{self.name}'


class Genre(models.Model):
    name = models.CharField(max_length=64,)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f'{self.name}'


class Title(models.Model):
    name = models.CharField(max_length=64)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='title'
    )
    description = models.TextField(null=True, blank=True)
    genre = models.ManyToManyField(Genre, through='TitleGenre', blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)


class TitleGenre(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Заголовок отзыва'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
        verbose_name='Оценка')

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )


class Comments(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
