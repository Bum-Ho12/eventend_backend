from dataclasses import field
from .models import  (Account,Concert,Service,Ticket,Request,FavoriteConcert,FavoriteService,ConcertComplaint,ServiceComplaint)
from rest_framework import serializers

class AccountSerializer(serializers.ModelSerializer):

    class  Meta:
        model = Account
        fields =    ['email','username', 'password','profile_picture',
                    'description','website','location','long','lat','phone_number','isCustomer'
                    ,'social_media_link','category','weekday_from','weekday_to','from_hour','to_hour']
        extra_kwargs = {
            'password': {'write_only':True},

            'media': {
                'required': False,
            }
        }
        def save(self,validated_data):
            account = Account.objects.create_user(
                validated_data['email'],
                validated_data['username'],
            )

            account.set_password(validated_data['password'])
            account.save()
            return account

class ConcertSerializer(serializers.ModelSerializer):
    concert = serializers.SerializerMethodField('get_concert')
    class Meta:
        model = Concert
        fields = ['id','title','concert','description','price','long','lat','from_hour','to_hour',
            'web_link','traffic','concert_picture','event_date','location' ,'tickets','advertise','reports']
        depth=1
    def get_concert(self, concert):
            concert = {
                'organizer_id':concert.owner.id,
                'organizer': concert.owner.username,
                'organizer_profile_picture':concert.owner.profile_picture.url,
                # 'organizer_media_link': concert.owner.social_media_link,
            }
            return concert

class ServiceSerializer(serializers.ModelSerializer):
    service = serializers.SerializerMethodField('get_service')
    class Meta:
        model = Service
        fields = ['id','title','service','description','price','long','lat' ,
            'permit','web_link','traffic','advertise','reports' ]
        depth=1
    def get_service(self, service):
            service = {
                'organizer_id':service.owner.id,
                'organizer': service.owner.username,
                'organizer_profile_picture':service.owner.profile_picture.url,
                'organizer_media_link': service.owner.social_media_link,
                'phone_number':service.owner.phone_number,
                'email':service.owner.email,
            }
            return service

class RequestSerializer(serializers.ModelSerializer):
    recipient = serializers.SerializerMethodField('get_recipient')
    client    = serializers.SerializerMethodField('get_client')
    service   = serializers.SerializerMethodField('get_service')
    class Meta:
        model = Request
        fields = ['recipient','id','service','client','description','viewed']
        depth=1
    def get_client(self, request):
            request = {
                'client_id':request.client.id,
                'client': request.client.username,
                'client_profile_picture':request.client.profile_picture.url,
                'client_number': request.client.phone_number,
            }
            return request

    def get_recipient(self, request):
            request = {
                'recipient_id':request.recipient.id,
                'recipient': request.recipient.username,
                'recipient_profile_picture':request.recipient.profile_picture.url,
                'recipient_number': request.recipient.phone_number,
            }
            return request

    def get_service(self, request):
            request = {
                'service_id':request.service.id,
                'service_title': request.service.title,
                'description': request.service.description,
                'price': request.service.price,
                'permit': request.service.permit.url,
            }
            return request

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket

        fields = '__all__'
        depth=1

class FavoriteConcertSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField('get_owner')
    concert = serializers.SerializerMethodField('get_concert')
    class Meta:
        model = FavoriteConcert
        fields = ['owner','id','concert',]

    def get_owner(self, favorite):
            favorite = {
                'organizer_id':favorite.owner.id,
                'organizer': favorite.owner.username,
                'organizer_profile_picture':favorite.owner.profile_picture.url,
                'organizer_media_link': favorite.owner.social_media_link,
            }
            return favorite

    def get_concert(self, favorite):
            favorite = {
                'concert_id':favorite.concert.id,
                'concert_title': favorite.concert.title,
                'concert_picture': favorite.concert.concert_picture.url,
                'event_date':favorite.concert.event_date,
                'from_hour':favorite.concert.from_hour,
                'to_hour':favorite.concert.to_hour,
                'location':favorite.concert.location,
                'long':favorite.concert.long,
                'lat':favorite.concert.lat,
                'description':favorite.concert.description,
                'price':favorite.concert.price,
                'traffic':favorite.concert.traffic,
                'tickets':favorite.concert.tickets,
            }
            return favorite

class FavoriteServiceSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField('get_owner')
    service = serializers.SerializerMethodField('get_service')
    class Meta:
        model = FavoriteService
        fields = ['owner','id','service']

    def get_owner(self, favorite):
            favorite = {
                'organizer_id':favorite.owner.id,
                'organizer': favorite.owner.username,
                'organizer_profile_picture':favorite.owner.profile_picture.url,
                'phone_number':favorite.owner.phone_number,
                'email':favorite.owner.email,
            }
            return favorite

    def get_service(self, favorite):
            favorite = {
                'service_id':favorite.service.id,
                'service_title': favorite.service.title,
                'service_owner_profile':favorite.service.owner.profile_picture.url,
                'organizer_media_link': favorite.service.owner.social_media_link,
                'phone_number':favorite.service.owner.phone_number,
                'email':favorite.service.owner.email,
                'long': favorite.service.long,
                'lat': favorite.service.lat,
                'description': favorite.service.description,
                'price': favorite.service.price,
                'permit': favorite.service.permit.url,
                'traffic': favorite.service.traffic,
            }
            return favorite

class ConcertComplaintSerializer(serializers.ModelSerializer):
    complainant = serializers.SerializerMethodField('get_user')
    concert   = serializers.SerializerMethodField('get_concert')
    class Meta:
        model = ConcertComplaint
        fields = ['id','complainant','description','concert']
        depth=1
    def get_user(self, request):
            request = {
                'complainant_id':request.owner.id,
                'name': request.owner.username,
                'profile_picture':request.owner.profile_picture.url,
                'phone_number': request.owner.phone_number,
            }
            return request
    def get_concert(self, request):
            request = {
                'concert_id':request.concert.id,
                'concert_title': request.concert.title,
                'description': request.concert.description,
                'price': request.concert.price,
                'owner': request.concert.owner.email,
            }
            return request

class ServiceComplaintSerializer(serializers.ModelSerializer):
    complainant = serializers.SerializerMethodField('get_user')
    service   = serializers.SerializerMethodField('get_service')
    class Meta:
        model = ServiceComplaint
        fields = ['id','complainant','service','description']
        depth=1
    def get_user(self, request):
            request = {
                'complainant_id':request.owner.id,
                'name': request.owner.username,
                'profile_picture':request.owner.profile_picture.url,
                'phone_number': request.owner.phone_number,
            }
            return request
    def get_service(self, request):
            request = {
                'service_id':request.service.id,
                'service_title': request.service.title,
                'description': request.service.description,
                'price': request.service.price,
                'permit': request.service.permit.url,
            }
            return request

