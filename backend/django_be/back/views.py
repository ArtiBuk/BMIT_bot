from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User,Projects, Report
from rest_framework.serializers import ModelSerializer

class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id','name']

class UserSerializer(ModelSerializer):
    projects = ProjectSerializer(many=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'birthday', 'tg_id', 'projects','id']
        
class ReportSerializer(ModelSerializer):
    class Meta:
        model = Report
        fields = ['date', 'hours', 'user', 'project']


@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_report(request):
    serializer = ReportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

