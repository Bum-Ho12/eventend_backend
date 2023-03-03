from django.shortcuts import render
from django.core.mail import  send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.permissions import  IsAuthenticated, AllowAny
from .models import (Account,Service,Concert,Ticket,Request)
from .serializers import (AccountSerializer,ServiceSerializer,TicketSerializer,ConcertSerializer,RequestSerializer)
from  rest_framework.authtoken.models import Token
from rest_framework import status
from  rest_framework.parsers import MultiPartParser, FormParser
import random
# Create your views here.
def activateEmail(user,to_email,code):
    send_mail(
        'Account Activation',
        'Dear ' + user + ', Welcome to Hovelink. To complete Your registration,\n \
                    Enter this Code: '+ str(code),
        'settings.EMAIL_HOST_USER',
        [to_email],
        fail_silently= False
    )

# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def registration_view(request):
    if request.method == 'POST':
        serialized = AccountSerializer(data=request.data)
        data = {}
        if serialized.is_valid():
            account = serialized.save()
            obj = Account.objects.get(email=account.email)
            code = random.randint(1000,9999)
            obj.verification_code = code
            obj.is_active = False
            obj.profile_picture = request.FILES.get('profile_picture')
            obj.save()
            activateEmail(account.username,account.email,code)
            data['response'] = "successfully registered a new user"
            data['email'] = account.email
            data['username'] = account.username
            if obj.profile_picture:
                data['profile_picture'] = obj.profile_picture.url
            token = Token.objects.get(user=account).key
            data['token'] = token
        else :
            data = serialized.errors
        return Response(data)

# function to verify email and activate user
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def verify_user(request):
    data={}
    email = request.data.get('email')
    code = request.data.get('verification_code')
    code = int(code)
    if request.method  == 'POST':
        owner = Account.objects.get(email = email)
        if owner.verification_code == code:
            owner.is_active = True
            owner.save()
            data['response'] = "successfully Activated your Account"
        else:
            data['response'] = "Wrong code Entered, request for verification again."

        return Response(data=data, status= status.HTTP_200_OK)

# request verification again function
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def re_verification(request):
    data={}
    email = request.data.get('email')
    code = random.randint(1000,9999)
    if request.method == 'POST':
        owner = Account.objects.get(email = email)
        if owner.email == email:
            owner.verification_code = code
            activateEmail(owner.username,owner.email,code)
            data['response'] = 'The verification code has been sent to your email address, {email}.'
        else:
            data['response'] = 'Oops!, There is an error in the verification process.'

        return Response(data=data, status= status.HTTP_200_OK)


# updates the details of the user
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def user_update_view(request):
    if request.method == 'PUT':
        owner = Account.objects.get(email=request.user.email)
        serialized = AccountSerializer(owner,data=request.data,partial=True)
        data = {}
        if serialized.is_valid():
            account= serialized.save()
            obj = Account.objects.get(email=account.email)
            if request.FILES.get('profile_picture'):
                Account.objects.get(email=account.email).profile_picture.delete(save=True)
                obj.profile_picture = request.FILES.get('profile_picture')
                obj.save()
            data['email'] = account.email
            data['username'] = account.username
            data['category'] = account.category
            if obj.profile_picture:
                data['profile_pic'] = obj.profile_picture.url
            token = Token.objects.get(user=account).key
            data['token'] = token
            data['response'] = "successfully updated Account"
            return Response(data = data, status=status.HTTP_200_OK)
        else :
            data = serialized.errors
            return Response(data = data, status=status.HTTP_406_NOT_ACCEPTABLE)

#logs user in the system
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def custom_login(request):
    data = request.data
    try:
        email = data['email']
        password = data['password']
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        user = Account.objects.get(email=email, password=password)
    except:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        user_token = user.auth_token.key
    except:
        user_token = Token.objects.create(user=user)
    data = {'token': user_token}
    data['email'] = user.email
    data['username'] = user.username
    data['profile_pic'] = user.profile_picture.url
    return Response(data=data, status=status.HTTP_200_OK)

#deletes user profile
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def userDelete_view(request):
    data={}
    try:
        owner = Account.objects.get(email=request.user.email)
    except Account.DoesNotExist:
        data['response'] = 'no such user in the database'
        return Response(data=data,status=status.HTTP_404_NOT_FOUND)
    if request.method=='DELETE':
        check   = owner
        operation=check.delete()
        if operation:
            data    = 'deleted Account successfully'
            return Response(data=data)
        else:
            data    = 'no such record in the database'
        return Response(data=data)

#logs user out of the  system
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()
    data={}
    data['success'] = 'successfully signed out'
    return Response(data=data,status=status.HTTP_200_OK)


# for creating an Ad post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def concert_create_post(request):
    user = request.user
    print(user.username)
    if request.method == 'POST':
        files = request.FILES.get('concert_picture')
        try:
            sr= ConcertSerializer
            if files:
                request.data.pop('concert_picture')
                serializer = sr(data=request.data)
                if serializer.is_valid():
                    qs = serializer.save()
                    qs.organizer = user.username
                    qs.organizer_id = user.pk
                    qs.organizer_profile_picture = user.profile_picture.url
                    qs.concert_picture = request.FILES.get('concert_picture')
                    qs.save()
                    context = serializer.data
                    context["concert_picture"] = qs.concert_picture.url
                    return Response(context, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = sr(data=request.data)
                if serializer.is_valid():
                    qs = serializer.save()
                    qs.organizer = user.username
                    qs.organizer_id = user.id
                    qs.organizer_profile_picture = user.profile_picture.url
                    context = serializer.data
                    return Response(context, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            rep = {}
            rep['response'] = 'no such record in the database'
            return Response(data=rep,status=status.HTTP_404_NOT_FOUND)

    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


#updates post
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def concert_update_post(request):
    user = request.user
    info = request.data.get('id')
    files = request.FILES.get('concert_picture')
    if request.method =='PUT':
        try:
            model_class = Concert
            sr= ConcertSerializer
            concert = Concert.objects.get(id=info)
            if files:
                request.data.pop('concert_picture')
                serializer = sr(concert,data=request.data,partial=True)
                if serializer.is_valid():
                    qs = serializer.save()
                    qs.organizer = user.username
                    qs.organizer_id = user.pk
                    qs.organizer_profile_picture = user.profile_picture.url
                    qs.concert_picture = request.FILES.get('concert_picture')
                    qs.save()
                    context = serializer.data
                    context["concert_picture"] = qs.concert_picture.url
                    return Response(context, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = sr(concert,data=request.data,partial=True)
                if serializer.is_valid():
                    qs = serializer.save()
                    qs.organizer = user.username
                    qs.organizer_id = user.pk
                    qs.organizer_profile_picture = user.profile_picture.url
                    qs.save()
                    context = serializer.data
                    return Response(context, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            rep = {}
            rep['response'] = 'no such record in the database'
            return Response(data=rep,status=status.HTTP_404_NOT_FOUND)
    data={}
    data['response']='failed to update'
    return Response( data=data,status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def service_create_post(request):
    user = request.user
    print(user.username)
    if request.method == 'POST':
        try:
            sr= ServiceSerializer
            serializer = sr(data=request.data)
            if serializer.is_valid():
                qs = serializer.save()
                qs.organizer = user.username
                qs.organizer_id = user.id
                qs.organizer_profile_picture = user.profile_picture.url
                context = serializer.data
                return Response(context, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            rep = {}
            rep['response'] = 'no such record in the database'
            return Response(data=rep,status=status.HTTP_404_NOT_FOUND)

    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


#updates post
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def service_update_post(request):
    user = request.user
    info = request.data.get('id')
    if request.method =='PUT':
        try:
            sr= ServiceSerializer
            service = Service.objects.get(id=info)
            serializer = sr(service,data=request.data,partial=True)
            if serializer.is_valid():
                qs = serializer.save()
                qs.organizer = user.username
                qs.organizer_id = user.pk
                qs.organizer_profile_picture = user.profile_picture.url
                qs.save()
                context = serializer.data
                return Response(context, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            rep = {}
            rep['response'] = 'no such record in the database'
            return Response(data=rep,status=status.HTTP_404_NOT_FOUND)
    data={}
    data['response']='failed to update'
    return Response( data=data,status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def request_send(request):
    user = request.user
    if request.method == 'POST':
        try:
            sr= RequestSerializer
            serializer = sr(data=request.data)
            if serializer.is_valid():
                qs = serializer.save()
                qs.client_name = user.username
                qs.client_id = user.id
                qs.client_profile_picture = user.profile_picture.url
                qs.phone_number = user.phone_number
                qs.save()
                context = serializer.data
                return Response(context, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            rep = {}
            rep['response'] = 'no such record in the database'
            return Response(data=rep,status=status.HTTP_404_NOT_FOUND)

    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def ticketing(request):
    user = request.user
    if request.method == 'POST':
        try:
            sr= TicketSerializer
            serializer = sr(data=request.data)
            if serializer.is_valid():
                # ['title','concert_id','concert_picture','assignee_id','assignee_name',
                #     'ticket_number','assignee_email','status','description','client']
                ticket_number = random.randint(1000,9999)
                qs = serializer.save()
                qs.ticket_number = ticket_number
                qs.assignee_name = user.username
                qs.assignee_id = user.id
                qs.assignee_email = user.email
                qs.assignee_picture = user.profile_picture.url
                qs.phone_number = user.phone_number
                qs.save()
                context = serializer.data
                return Response(context, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            rep = {}
            rep['response'] = 'no such record in the database'
            return Response(data=rep,status=status.HTTP_404_NOT_FOUND)

    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# deletes an Ad
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def all_delete(request):
    info = request.data.get('id')
    choice = request.data.get('choice')
    data={}
    try:
        if choice=='concert':
            owner = Concert.objects.get(id=info)
        elif choice=='service':
            owner = Service.objects.get(id=info)
        else:
            data['response']= 'Choice required'
    except owner.DoesNotExist:
        data['response'] = 'no such record in the database'
        return Response(data=data,status=status.HTTP_404_NOT_FOUND)
    if request.method=='DELETE':
        check=owner
        operation=check.delete()
        if operation:
            data['response']='deleted successfully'
        else:
            data['response'] = 'no such record in the database'
        return Response(data=data)

