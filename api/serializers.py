from dataclasses import field
from .models import  (Account,Concert,Service,Ticket,Request)
from rest_framework import serializers

class AccountSerializer(serializers.ModelSerializer):

    class  Meta:
        model = Account
        fields =    ['email','username', 'password','profile_picture',
                    'description','website','location','long','lat','phone_number'
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
            'web_link','traffic','concert_picture','event_date','location' ,'tickets']
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
            'permit','web_link','traffic' ]
        depth=1
    def get_service(self, service):
            service = {
                'organizer_id':service.owner.id,
                'organizer': service.owner.username,
                'organizer_profile_picture':service.owner.profile_picture.url,
                'organizer_media_link': service.owner.social_media_link,
            }
            return service

class RequestSerializer(serializers.ModelSerializer):
    # service = serializers.SerializerMethodField('get_request')
    class Meta:
        model = Request
        fields = '__all__'
        depth=1
        # def get_request(self, request):
        #     request = {
        #         'organizer_id':request.user.id,
        #         'organizer': request.user.username,
        #         'organizer_profile_picture':request.user.profile_picture,
        #         'organizer_media_link': request.user.social_media_link,
        #     }
        #     return request

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket

        fields = ['title','concert_id','concert_picture','assignee_id','assignee_name','assignee_picture',
                    'ticket_number','assignee_email','status','description','client','phone_number']
        depth=1


