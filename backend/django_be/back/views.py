from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Projects, Report
from rest_framework.serializers import ModelSerializer
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "birthday",
            "tg_id",
            "id",
        ]


class ProjectSerializer(ModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Projects
        fields = ["id", "name", "short_description", "users"]


class ReportSerializer(ModelSerializer):
    class Meta:
        model = Report
        fields = ["date", "hours", "user", "project", "text_report"]


@api_view(["POST"])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def create_report(request):
    serializer = ReportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def view_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def view_projects(request):
    projects = Projects.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def view_report(request):
    # Получение параметров запроса
    project_name = request.query_params.get("project_name")
    hours = request.query_params.get("hours")
    date = request.query_params.get("date")
    user_id = request.query_params.get("user_id")

    # Фильтрация данных отчета
    reports = Report.objects.all()

    if project_name:
        reports = reports.filter(project__name=project_name)

    if hours:
        reports = reports.filter(hours=hours)

    if date:
        reports = reports.filter(date=date)

    if user_id:
        reports = reports.filter(user_id=user_id)

    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@login_required
def report_view(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date = datetime.strptime(start_date, '%d.%m.%Y').date()
        end_date = datetime.strptime(end_date, '%d.%m.%Y').date()

        # Получение параметров фильтрации
        user_id = request.POST.get('user_id')
        project_id = request.POST.get('project_id')

        # Получение всех пользователей и проектов
        users = User.objects.all()
        projects = Projects.objects.all()

        # Создание заголовка таблицы
        table_header = ['Название проекта', 'Фамилия Имя Пользователя']
        current_date = start_date
        while current_date <= end_date:
            table_header.append(current_date.strftime('%d.%m.%Y'))
            current_date += timedelta(days=1)

        # Создание таблицы с данными
        table_data = []
        for project in projects:
            for user in project.users.all():
                if user_id and user_id != str(user.id):
                    continue
                if project_id and project_id != str(project.id):
                    continue
                row = [project.name, user.get_full_name()]
                current_date = start_date
                while current_date <= end_date:
                    total_hours = Report.objects.filter(
                        date=current_date,
                        user=user,
                        project=project
                    ).aggregate(Sum('hours')).get('hours__sum', 0)
                    row.append(total_hours or 0)
                    current_date += timedelta(days=1)
                table_data.append(row)

        context = {
            'table_header': table_header,
            'table_data': table_data,
            'users': users,
            'projects': projects
        }

        return render(request, 'report.html', context)
    else:
        users = User.objects.all()
        projects = Projects.objects.all()
        context = {
            'users': users,
            'projects': projects
        }
        return render(request, 'report.html', context)


