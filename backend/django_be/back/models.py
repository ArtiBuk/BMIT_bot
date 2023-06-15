from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    birthday = models.DateField(blank=True, null=True)
    tg_id = models.IntegerField(unique=True, null=True)
    projects = models.ManyToManyField("Projects", related_name="users", blank=True)

    def __str__(self):
        return self.username


class Projects(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name="Название проекта")
    short_description = models.CharField(
        max_length=64, blank=True, verbose_name="Краткое описание"
    )

    class Meta:
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name


class Report(models.Model):
    date = models.DateField(verbose_name="Дата")
    hours = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        verbose_name="Количество часов",
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    project = models.ForeignKey(
        Projects, on_delete=models.CASCADE, verbose_name="Проект"
    )
    text_report = models.TextField(verbose_name="Отчет")

    class Meta:
        verbose_name_plural = "Данные для отчета"

    def __str__(self):
        return f"{self.user.username} - {self.project.name}"
