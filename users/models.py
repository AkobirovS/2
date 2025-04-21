from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random

ROLES = (
    ('student', 'Ученик'),
    ('teacher', 'Учитель'),
    ('director', 'Директор'),
    ('admin', 'Админ'),
)

from django.db import transaction

class UserManager(BaseUserManager):
    @transaction.atomic
    def create_user(self, phone_number, role='student'):
        code = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        user = self.model(phone_number=phone_number, role=role, code=code)
        user.set_password(code)
        user.save()

        # Автоматически создаём студента или учителя
        if role == 'student':
            Student.objects.create(user=user)
        elif role == 'teacher':
            Teacher.objects.create(user=user)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    code = models.CharField(max_length=7, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLES, default='student')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return f'{self.phone_number} ({self.role})'


class Class(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)  # ← добавим класс
    grades = models.JSONField(default=list)
    has_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Ученик: {self.user.phone_number}"


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.JSONField(default=list)  # список предметов
    classes = models.ManyToManyField(Class)

    def __str__(self):
        return f"Учитель: {self.user.phone_number}"
