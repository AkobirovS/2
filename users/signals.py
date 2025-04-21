from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Student, Teacher
@receiver(post_save, sender=User)
def create_student(sender, instance, created, **kwargs):
    if created and instance.role == 'student':
        Student.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_related_profile(sender, instance, created, **kwargs):
    if instance.role == 'student' and not hasattr(instance, 'student'):
        Student.objects.create(user=instance)
    elif instance.role == 'teacher' and not hasattr(instance, 'teacher'):
        Teacher.objects.create(user=instance)