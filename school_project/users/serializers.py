from rest_framework import serializers
from .models import Student, Teacher, User, ROLES


class PhoneRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

class CodeLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class PhoneRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    role = serializers.ChoiceField(choices=ROLES, required=False)  # 👈 добавлено
