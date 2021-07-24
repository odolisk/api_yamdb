from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


class User(AbstractUser, PermissionsMixin):

    USER_ROLES = (
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin')
    )

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        help_text='Обязательное поле.Не более 150 символов.',
        error_messages={
            'unique': 'Пользователь с таким username уже существует.',
        },
    )

    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
        null=True)

    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
        null=True)

    email = models.EmailField(
        'email',
        unique=True,
        help_text='Email адрес. Должен быть уникальным.',
        error_messages={
            'unique': 'Пользователь с таким Email уже существует.',
        },)

    bio = models.TextField(
        'О себе',
        max_length=500,
        blank=True,
        null=True,
        help_text='О себе')

    role = models.CharField(
        'Роль',
        max_length=50,
        choices=USER_ROLES,
        default=USER,
        help_text='Роль')

    is_active = models.BooleanField(
        'Активен',
        default=1,
        help_text='Активен или нет')

    is_staff = models.BooleanField(
        'Сотрудник',
        default=0,
        help_text='Является ли сотрудником')

    is_superuser = models.BooleanField(
        'Суперпользователь',
        default=0,
        help_text='Суперпользователь')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email',)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app?"""
        return True

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_administrator(self):
        return self.role == ADMIN


class Category(models.Model):
    name = models.CharField('Название', max_length=64)
    slug = models.SlugField('Slug', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Название', max_length=64,)
    slug = models.SlugField('Slug', unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Название', max_length=64)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория',
        related_name='title'
    )
    description = models.TextField('Описание', blank=True)
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        verbose_name='Жанр')
    year = models.PositiveSmallIntegerField(
        'Год создания', null=True, blank=True)
    rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='Рейтинг',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('category',)),
            models.Index(fields=('name',)),
            models.Index(fields=('year',)),
        ]

    def __str__(self):
        return self.name


# class TitleGenre(models.Model):
#     genre = models.ForeignKey(
#         Genre,
#         on_delete=models.CASCADE,
#         verbose_name='Жанр')
#     title = models.ForeignKey(
#         Title,
#         on_delete=models.CASCADE,
#         verbose_name='Произведение')

#     def __str__(self):
#         return f'{self.genre} {self.title}'

#     class Meta:
#         verbose_name = 'Жанр произведения'
#         verbose_name_plural = 'Жанры произведений'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
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

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-id',)

    def __str__(self):
        return self.text[:25]


class Comment(models.Model):
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

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-id',)

    def __str__(self):
        return self.text[:25]
