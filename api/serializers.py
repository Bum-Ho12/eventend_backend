from dataclasses import field
from .models import  (Account,Concert,Service,Ticket,Request)
from rest_framework import serializers

class AccountSerializer(serializers.ModelSerializer):

    class  Meta:
        model = Account
        fields =    ['email','username', 'password','profile_picture',
                    'description','website','location','services','concerts','long','lat','phone_number'
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
    class Meta:
        model = Concert
        fields = '__all__'
        depth=1

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
        depth=1

class RequestSerializer(serializers.ModelSerializer):
    # service = serializers.SerializerMethodField('get_service')
    class Meta:
        model = Request
        fields = '__all__'
        depth=1
        # def get_service(self, service):
        #     service = {
        #     'service_id': service.service_requested.id,
        #     'service_title': service.service_requested.title,
        #     }
        #     return service

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket

        fields = ['title','concert_id','concert_picture','assignee_id','assignee_name','assignee_picture',
                    'ticket_number','assignee_email','status','description','client','phone_number']
        depth=1


