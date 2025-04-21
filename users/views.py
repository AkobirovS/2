from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Student, Teacher
from .serializers import PhoneRegistrationSerializer, CodeLoginSerializer, StudentSerializer, TeacherSerializer
import random


# Регистрация по номеру телефона
class RegisterPhoneView(APIView):
    def post(self, request):
        serializer = PhoneRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            role = serializer.validated_data.get('role', 'student')  # Роль по умолчанию — student
            code = ''.join([str(random.randint(0, 9)) for _ in range(7)])

            # Получаем или создаем пользователя
            user, created = User.objects.get_or_create(phone_number=phone)
            user.code = code
            user.role = role  # Присваиваем роль
            user.set_password(code)
            user.save()

            # Если пользователь только что создан — создаём профиль
            if created:
                if user.role == 'student':
                    Student.objects.create(user=user)
                elif user.role == 'teacher':
                    Teacher.objects.create(user=user)

            return Response({"message": "Код отправлен", "code": code}, status=201)
        return Response(serializer.errors, status=400)


# Логин с кодом
class LoginWithCodeView(APIView):
    def post(self, request):
        serializer = CodeLoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']
            try:
                user = User.objects.get(phone_number=phone)
                if user.code == code:
                    return Response({"message": "Успешный вход", "role": user.role}, status=200)
                else:
                    return Response({"error": "Неверный код"}, status=400)
            except User.DoesNotExist:
                return Response({"error": "Пользователь не найден"}, status=404)
        return Response(serializer.errors, status=400)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User, Student, Teacher
from .serializers import StudentSerializer, TeacherSerializer

class DashboardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        phone_number = request.query_params.get('phone_number')
        if not phone_number:
            return Response({"error": "Номер телефона обязателен"}, status=400)

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=404)

        role = user.role

        if role == 'student':
            if not hasattr(user, 'student'):
                return Response({"error": "Пользователь не привязан к модели Student"}, status=400)
            data = StudentSerializer(user.student).data
            return Response({"role": role, "data": data})

        elif role == 'teacher':
            if not hasattr(user, 'teacher'):
                return Response({"error": "Пользователь не привязан к модели Teacher"}, status=400)
            data = TeacherSerializer(user.teacher).data
            return Response({"role": role, "data": data})

        elif role == 'director':
            students = Student.objects.all()
            data = [
                {"phone_number": s.user.phone_number, "grades": s.grades} for s in students
            ]
            return Response({"role": role, "data": data})

        elif role == 'admin':
            return Response({"role": role, "message": "Панель администратора (в разработке)"})

        return Response({"error": "Неизвестная роль"}, status=400)

# Обновление оценок
class GradeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone = request.data.get('student_phone')
        subject = request.data.get('subject')
        grade = request.data.get('grade')

        if not (phone and subject and grade):
            return Response({"error": "Заполните все поля"}, status=400)

        try:
            student_user = User.objects.get(phone_number=phone)
            student = Student.objects.get(user=student_user)
        except (User.DoesNotExist, Student.DoesNotExist):
            return Response({"error": "Ученик не найден"}, status=404)

        # добавляем оценку в формат {"math": [5, 4], "history": [3]}
        current_grades = student.grades
        if subject not in current_grades:
            current_grades[subject] = []

        current_grades[subject].append(grade)
        student.grades = current_grades
        student.save()

        return Response({"message": "Оценка добавлена успешно"})


# Получение JWT токенов
class CustomTokenObtainPairView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone_number')
        code = request.data.get('code')
        try:
            user = User.objects.get(phone_number=phone)
            if user.code != code:
                return Response({"error": "Неверный код"}, status=400)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=404)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role
        })

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Student, Class

class AssignClassToStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        class_id = request.data.get("class_id")
        student_ids = request.data.get("student_ids")

        if not class_id or not student_ids:
            return Response({"error": "class_id и student_ids обязательны"}, status=400)

        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"error": "Класс не найден"}, status=404)

        updated_count = Student.objects.filter(id__in=student_ids).update(student_class=class_obj)

        return Response({"message": f"{updated_count} учеников добавлены в класс {class_obj.name}"})
