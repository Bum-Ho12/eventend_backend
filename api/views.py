import codecs
from django.core.files.base import ContentFile
from django.core.files import File
from django.core.mail import  send_mail,EmailMessage
from collections import OrderedDict
from rest_framework import generics,filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.permissions import  IsAuthenticated, AllowAny
from .models import (Account,Service,Concert,Ticket,Request,FavoriteConcert,FavoriteService)
from .serializers import (AccountSerializer,ServiceSerializer,TicketSerializer,ConcertSerializer,RequestSerializer,
    FavoriteConcertSerializer,FavoriteServiceSerializer)
from  rest_framework.authtoken.models import Token
from rest_framework import status
from  rest_framework.parsers import MultiPartParser, FormParser
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch,cm
from django.conf import settings
from reportlab.lib.pagesizes import HALF_LETTER
import random
import string


#network confirmation
@api_view(['GET'])
@permission_classes([AllowAny])
def confirmNetwork(request):
    if request.method =='GET':
        return Response(data=True,status=status.HTTP_200_OK)

# to send verification email.
def activateEmail(user,to_email,code):
    send_mail(
        'Account Activation',
        'Dear ' + user + ', Welcome to Eventend. To complete Your registration,\n \
                    Enter this Code: '+ str(code),
        'settings.EMAIL_HOST_USER',
        [to_email],
        fail_silently= False
    )

def sendEmail(cs,user,to_email,id):
    subject = 'Concert Ticket'
    message = 'Dear ' + user + ', Thank you for trusting us,\n \
                    Here is your ticket.'
    mail= EmailMessage(subject,message,settings.EMAIL_HOST_USER,[to_email])
    mail.attach(cs.name, cs.read())
    mail.send()
    obj = Concert.objects.get(id = id)
    obj.tickets = obj.tickets+1
    obj.save()

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
            data['category'] = account.category
            data['location']=account.location
            data['weekday_from']=account.weekday_from
            data['weekday_to']=account.weekday_to
            data['from_hour']=account.from_hour
            data['to_hour']=account.to_hour
            data['social_media_link']=account.social_media_link
            data['description']=account.description
            data['phone_number']=account.phone_number
            data['isCustomer']=account.isCustomer
            data['long']=account.long
            data['lat']=account.lat
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
                data['profile_picture'] = obj.profile_picture.url
            data['category'] = account.category
            token = Token.objects.get(user=account).key
            data['token'] = token
            data['location']=account.location
            data['weekday_from']=account.weekday_from
            data['weekday_to']=account.weekday_to
            data['from_hour']=account.from_hour
            data['to_hour']=account.to_hour
            data['social_media_link']=account.social_media_link
            data['description']=account.description
            data['phone_number']=account.phone_number
            data['isCustomer']=account.isCustomer
            data['long']=account.long
            data['lat']=account.lat
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
    data['profile_picture'] = user.profile_picture.url
    data['category'] = user.category
    data['location']=user.location
    data['weekday_from']=user.weekday_from
    data['weekday_to']=user.weekday_to
    data['from_hour']=user.from_hour
    data['to_hour']=user.to_hour
    data['social_media_link']=user.social_media_link
    data['description']=user.description
    data['phone_number']=user.phone_number
    data['isCustomer']=user.isCustomer
    data['long']=user.long
    data['lat']=user.lat
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


# code for getting each category of posts
@api_view(['GET'])
@permission_classes([AllowAny])
def category_view(request):
    category = request.data.get('category')
    try:
        if category=='concerts':
            owner = Concert.objects.all()
            sr= ConcertSerializer(owner, many=True)
            data = sr.data
            res = reversed(data)
            return Response(data=res,status=status.HTTP_200_OK)
        elif category=='services':
            owner = Service.objects.all()
            sr= ServiceSerializer(owner, many=True)
            data = sr.data
            res = reversed(data)
            return Response(data=res,status=status.HTTP_200_OK)
    except category.IsEmpty:
        data = {}
        data['response'] = 'no such record in the database'
        return Response(data=data,status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_200_OK)


# for creating an Ad post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def concert_create_post(request):
    user = request.user
    if request.method == 'POST':
        files = request.FILES.get('concert_picture')
        try:
            sr= ConcertSerializer
            if user.isCustomer == False:
                try:
                    obj = Concert.objects.filter(owner = user).count()
                    # print(obj)
                    if user.category==2 and obj==5:
                        rep = 'you can only have 5 posts'
                        return Response(data=rep,status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        if files:
                            request.data.pop('concert_picture')
                            serializer = sr(data=request.data)
                            if serializer.is_valid():
                                serializer.save(owner = user)
                                obj = Concert.objects.get(id=serializer.data['id'])
                                context = serializer.data
                                obj.concert_picture = request.FILES.get('concert_picture')
                                obj.save()
                                context['concert_picture'] = obj.concert_picture.url
                                return Response(context, status=status.HTTP_201_CREATED)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            serializer = sr(data=request.data)
                            if serializer.is_valid():
                                serializer.save(owner = user)
                                context = serializer.data
                                return Response(context, status=status.HTTP_201_CREATED)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except:
                    if files:
                            request.data.pop('concert_picture')
                            serializer = sr(data=request.data)
                            if serializer.is_valid():
                                serializer.save(owner = user)
                                obj = Concert.objects.get(id=serializer.data['id'])
                                context = serializer.data
                                obj.concert_picture = request.FILES.get('concert_picture')
                                obj.save()
                                context['concert_picture'] = obj.concert_picture.url
                                return Response(context, status=status.HTTP_201_CREATED)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        serializer = sr(data=request.data)
                        if serializer.is_valid():
                            serializer.save(owner = user)
                            context = serializer.data
                            return Response(context, status=status.HTTP_201_CREATED)
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            rep = {}
            rep['response'] = 'Error adding post'
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
            sr= ConcertSerializer
            concert = Concert.objects.get(id=info)
            if user.isCustomer == False:
                if files:
                    request.data.pop('concert_picture')
                    serializer = sr(concert,data=request.data,partial=True)
                    if serializer.is_valid():
                        serializer.save(owner = user)
                        obj = Concert.objects.get(id=serializer.data['id'])
                        context = serializer.data
                        obj.concert_picture = request.FILES.get('concert_picture')
                        obj.save()
                        context['concert_picture'] = obj.concert_picture.url
                        return Response(context, status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializer = sr(concert,data=request.data,partial=True)
                    if serializer.is_valid():
                        serializer.save(owner = user)
                        context = serializer.data
                        return Response(context, status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # print(e)
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
    if request.method == 'POST':
        try:
            if user.isCustomer == False:
                try:
                    obj = Service.objects.filter(owner = user).count()
                    # print(obj)
                    if user.category==1 and obj==1:
                        rep = 'you can only post once'
                        return Response(data=rep,status=status.HTTP_406_NOT_ACCEPTABLE)
                    elif user.category==2 and obj==5:
                        rep = 'you can only have 5 posts'
                        return Response(data=rep,status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        sr= ServiceSerializer
                        serializer = sr(data=request.data)
                        if serializer.is_valid():
                            serializer.save(owner = user)
                            context = serializer.data
                            return Response(context, status=status.HTTP_201_CREATED)
                        return Response(context, status=status.HTTP_401_UNAUTHORIZED)
                except:
                    sr= ServiceSerializer
                    serializer = sr(data=request.data)
                    if serializer.is_valid():
                        serializer.save(owner = user)
                        context = serializer.data
                        return Response(context, status=status.HTTP_201_CREATED)
                    return Response(context, status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            rep = {}
            rep['response'] = 'Error adding post'
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
            if user.isCustomer == False:
                sr= ServiceSerializer
                service = Service.objects.get(id=info)
                serializer = sr(service,data=request.data,partial=True)
                if serializer.is_valid():
                    serializer.save(owner = user)
                    context = serializer.data
                    return Response(context, status=status.HTTP_201_CREATED)
                return Response(context, status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except :
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
    recipient_id = request.data.get('id')
    service_id = request.data.get('service_id')
    if request.method == 'POST':
        try:
            recipient = Account.objects.get(id= recipient_id)
            service = Service.objects.get(id = service_id)
            if service.owner.email == user.email:
                context = 'You are not Allowed to send a request'
                return Response(context, status=status.HTTP_201_CREATED)
            else:
                sr= RequestSerializer
                serializer = sr(data=request.data)
                if serializer.is_valid():
                    serializer.save(client = user,recipient=recipient,service = service)
                    context = serializer.data
                    return Response(context, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            rep = {}
            rep['response'] = 'no such record in the database'
            return Response(data=rep,status=status.HTTP_404_NOT_FOUND)

    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def get_user_requests(request):
    user = request.user
    if request.method =='GET':
        try:
            requests = Request.objects.filter(recipient = user)
            sr       = RequestSerializer(requests,many=True)
            data = sr.data
            res = reversed(data)
            return Response(data=res,status=status.HTTP_200_OK)
        except Exception as e:
            data = {}
            data['response'] = str(e)
            return Response(data=data,status=status.HTTP_404_NOT_FOUND)

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
        elif choice == 'favorite_service':
            owner = FavoriteService.objects.get(id = info)
        elif choice =='favorite_concert':
            owner = FavoriteConcert.objects.get(id=info)
        else:
            data['response']= 'Choice required'
    except owner.DoesNotExist:
        data['response'] = 'no such record in the database'
        return Response(data=data,status=status.HTTP_204_NO_CONTENT)
    if request.method=='DELETE':
        check=owner
        operation=check.delete()
        if operation:
            data['response']='deleted successfully'
        else:
            data['response'] = 'no such record in the database'
        return Response(data=data)

# codes for getting each category of favorites
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def concert_favorite_view(request):
    try:
        owner = FavoriteConcert.objects.filter(owner = request.user)
        sr= FavoriteConcertSerializer(owner, many=True)
        data = sr.data
        res = reversed(data)
        return Response(data=res,status=status.HTTP_200_OK)
    except Exception as e:
        data = {}
        data['response'] = str(e)
        return Response(data=data,status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def service_favorite_view(request):
    try:
        owner = FavoriteService.objects.filter(owner = request.user)
        sr= FavoriteServiceSerializer(owner, many=True)
        data = sr.data
        res = reversed(data)
        return Response(data=res,status=status.HTTP_200_OK)
    except Exception as e:
        data = {}
        data['response'] = str(e)
        return Response(data=data,status=status.HTTP_404_NOT_FOUND)


# adds an Ad to favorite
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorite(request):
    category = request.data.get('category')
    id = request.data.get('id')
    if request.method == 'POST':
        try:
            if category=='concert':
                concert_to_insert = Concert.objects.get(id = id)
                model = FavoriteConcert.objects.create(owner = request.user,concert = concert_to_insert)
                sr = FavoriteConcertSerializer(model)
            elif category =='service':
                service_to_insert = Service.objects.get(id = id)
                model = FavoriteService.objects.create(owner = request.user,service = service_to_insert)
                sr = FavoriteServiceSerializer(model)
            else:
                return Response(data= 'error in category')
            data = sr.data
            return Response(data=data,status=status.HTTP_201_CREATED)
        except Exception as e:
            rep = {}
            rep['response'] = str(e)
            return Response(data=rep,status=status.HTTP_404_NOT_FOUND)

    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

# search functionality
class SearchConcerts(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'price','owner__username']
    filter_backends = (filters.SearchFilter, )
    queryset = Concert.objects.all()
    serializer_class = ConcertSerializer

class SearchServices(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'price','owner__username']
    filter_backends = (filters.SearchFilter, )
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

# adds an Ad to favorite
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_posts(request):
    user = request.user
    data={}
    concert_query       = Concert.objects.filter(owner= user.id)
    service_query       = Service.objects.filter(owner = user.id)
    #serializing
    concert_sr          = ConcertSerializer(concert_query,many = True)
    service_sr          = ServiceSerializer(service_query,many = True)
    #add to dictionary
    data['concerts']    = concert_sr.data
    data['services']    = service_sr.data
    #reverse the dictionary
    res = OrderedDict(reversed(list(data.items())))
    return Response(data = res,status=status.HTTP_200_OK)


# send views count and notification feedback
@api_view(['POST'])
@permission_classes([AllowAny])
def confirmFeedBack(request):
    option = request.data.get('option')
    id     = request.data.get('id')
    if request.method =='POST':
        if option == 'notification':
            request = Request.objects.get(id=id)
            viewed = True
            request.viewed = viewed
            request.save()
            context = {'response':True}
            return Response(context, status=status.HTTP_201_CREATED)
        elif option=='service':
            service = Service.objects.get(id=id)
            count = service.traffic
            count = count+1
            service.traffic = count
            service.save()
            context = {'response':True}
            return Response(context, status=status.HTTP_201_CREATED)
        elif option =='concert':
            concert = Concert.objects.get(id=id)
            count = concert.traffic
            count = count+1
            concert.traffic = count
            concert.save()
            context = {'response':True}
        else:
            context = {'response':'error'}
            return Response(context, status=status.HTTP_404_NOT_FOUND)


def ticket_generate(id,concert):
    ticket = Ticket.objects.get(id = id)
    try:
        buf = io.BytesIO()
        cs = canvas.Canvas(buf,pagesize=HALF_LETTER)
        txt_object = cs.beginText(1, 100)
        txt_object.setTextOrigin(0.7*inch,5*inch)
        txt_object.setFont('Helvetica',14)
        ticket_title = f"Concert Title: {ticket.concert.title}"
        ticket_number = f"Ticket: {ticket.ticket_number}"
        ticket_name = f"Name of recipient: {ticket.assignee.username}"
        content = [
            ticket_title,
            ticket_number,
            ticket_name,
            f"Bought at: {ticket.created_at}"
        ]
        for line in content:
            txt_object.textLine(line)
            txt_object.textLine('=================================')
        # in development is http://127.0.0.1:8000{ticket.assignee.profile_picture.url}
        # cs.drawImage(f'https://eventend.pythonanywhere.com{ticket.assignee.profile_picture.url}',0.8*inch,6 *inch,height=5*cm,width=5*cm)
        cs.drawText(txt_object)
        cs.showPage()
        cs.save()
        buf.seek(0)
        pdf = buf.getvalue()
        buf.close()
        ticket.receipt.save(f"./media/tickets/{ticket.assignee.username}{ticket.ticket_number}.pdf", ContentFile(pdf))
        ticket.save()
        sendEmail(ticket.receipt,ticket.assignee.username,ticket.assignee.email,concert)
    except :
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_ticket(request):
    user = request.user
    concert = Concert.objects.get(id = request.data.get('id'))
    code = random.randint(1000,9999)
    letter = random.choice(string.ascii_letters)
    ticket_number =  letter+str(code)
    if request.method == 'POST':
        obj = Ticket.objects.filter(assignee = user)
        if obj.exists():
            context ='Already have a ticket'
            return Response(context,status=status.HTTP_201_CREATED)
        else:
            if concert.owner.email ==user.email:
                context ='You are not Allowed to get a ticket'
                return Response(context,status=status.HTTP_201_CREATED)
            else:
                qs = Ticket.objects.create(ticket_number=ticket_number)
                qs.assignee = user
                qs.concert = concert
                qs.save()
                ticket_generate(qs.id,qs.concert.id)
                context = True
                return Response(context, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

