import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.forms import FileField
from  rest_framework.authtoken.models import Token
from  django.dispatch import  receiver
from django.conf import  settings
from  django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.files.storage import default_storage
from django.db.models.signals import post_delete

# models
class MyAccountManager(BaseUserManager):
    def create_user(self,email, username, password):

        if not email:
            raise  ValueError('user must have an email address.')
        if not username:
            raise  ValueError('user must have a username.')
        user =self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self,email,username,password):
        user = self.create_user(
            email = self.normalize_email(email),
            username=username,
            password=password,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

WEEKDAYS = [
    (1, _("Monday")),
    (2, _("Tuesday")),
    (3, _("Wednesday")),
    (4, _("Thursday")),
    (5, _("Friday")),
    (6, _("Saturday")),
    (7, _("Sunday")),
    ]
CATEGORY = [
    (1, _("Independent")),
    (2, _("Organization")),
    ]
TICKET_STATUS = [
    (1, _("Generate")),
    (2, _("In Progress")),
    (3, _("In Review")),
    (4, _("Done")),
    ]

class Account(AbstractBaseUser, PermissionsMixin):
    phone_regex                    = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number                   = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email                          = models.EmailField(max_length=60, verbose_name='email',unique=True)
    username                       = models.CharField(max_length=30, unique=True)
    profile_picture                = models.ImageField(blank=True)
    category                       = models.PositiveSmallIntegerField(choices=CATEGORY,null=True,blank=True)
    verification_code              = models.IntegerField(blank=True,null=True)
    website                        = models.CharField(blank = True,null=True,max_length=100,default='')
    social_media_link              = models.CharField(blank = True,null=True,max_length=100,default='')
    location                       = models.CharField(blank=True,null=True,max_length=100,default='')
    weekday_from                   = models.PositiveSmallIntegerField(choices=WEEKDAYS,null=True,default=1,
                                        blank=True)
    isCustomer                     = models.BooleanField(default=True,blank=True,null=True)
    weekday_to                     = models.PositiveSmallIntegerField(choices=WEEKDAYS,default=5,blank=True,
                                        null=True)
    from_hour                      = models.TimeField(null=True,blank = True,default='8:00:00')
    to_hour                        = models.TimeField(null=True,blank = True,default='17:00:00')
    long                           = models.DecimalField(max_digits=9, decimal_places=6,null=True,blank=True,default=1.00)
    lat                            = models.DecimalField(max_digits=9, decimal_places=6,null=True,blank = True,default=1.00)
    description                    = models.CharField(blank=True,null = True,max_length=400,default='')
    date_joined                    = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login                     = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin                       = models.BooleanField(default=False)
    is_active                      = models.BooleanField(default=True)
    is_staff                       = models.BooleanField(default=False)
    is_superuser                   = models.BooleanField(default=False)
    hide_email                     = models.BooleanField(default=True)

    objects = MyAccountManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def photo_url(self):
        if self.media and hasattr(self.media, 'url'):
            return self.media.url

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created = False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Concert(models.Model):
    title                       = models.CharField(max_length=100,blank=False)
    owner                       = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    concert_picture             = models.ImageField(blank=True)
    event_date                  = models.CharField(blank=False,max_length= 50)
    from_hour                   = models.TimeField()
    to_hour                     = models.TimeField()
    location                    = models.CharField(blank=True,null=True,max_length=100)
    long                        = models.DecimalField(max_digits=9, decimal_places=6)
    lat                         = models.DecimalField(max_digits=9, decimal_places=6)
    description                 = models.CharField(blank=True,null = True,max_length=400)
    price                       = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    web_link                    = models.CharField(blank=True,null = True, max_length=100)
    traffic                     = models.IntegerField(blank=True,default= 0)
    tickets                     = models.IntegerField(blank=True,default= 0)
    advertise                   = models.BooleanField(blank=True, null=True,default=True)
    reports                     = models.IntegerField(blank=True,null=True, default=0)

    class Meta:
        verbose_name_plural = 'Concerts'
    def  __str__(self):
        return f"{self.title}"

class Service(models.Model):
    title                       = models.CharField(max_length=100,blank=False)
    owner                       = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    description                 = models.CharField(blank=True,null = True,max_length=400)
    price                       = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    long                        = models.DecimalField(max_digits=9, decimal_places=6)
    lat                         = models.DecimalField(max_digits=9, decimal_places=6)
    permit                      = models.FileField(upload_to='certificates/',blank=True,null=True)
    web_link                    = models.CharField(blank=True,null = True, max_length=200)
    traffic                     = models.IntegerField(blank=True,default= 0)
    advertise                   = models.BooleanField(blank=True, null=True,default=True)
    reports                     = models.IntegerField(blank=True,null=True, default=0)

    class Meta:
        verbose_name_plural = 'Services'
    def  __str__(self):
        return f"{self.title}"

class Ticket(models.Model):
    concert                     = models.ForeignKey(Concert, on_delete = models.CASCADE,null=True)
    assignee                    = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='assignee',null=True)
    status                      = models.PositiveSmallIntegerField(
                                        choices=TICKET_STATUS, blank=True,null=True)
    receipt                     = models.FileField(upload_to='tickets/',blank=True,null=True)
    ticket_number               = models.TextField(blank=True,null=True)
    created_at                  = models.DateTimeField('created at', auto_now_add=True)
    updated_at                  = models.DateTimeField('updated at', auto_now=True)

    class Meta:
        verbose_name_plural = 'Tickets'
    def  __str__(self):
        return f"{self.ticket_number}"

class FavoriteConcert(models.Model):
    owner                       = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    concert                     = models.ForeignKey(Concert, on_delete = models.CASCADE)
    created_at                  = models.DateTimeField(auto_now_add=True,null=True)
    updated_at                  = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        verbose_name_plural = 'FavoriteConcerts'
class FavoriteService(models.Model):
    owner                       = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    service                     = models.ForeignKey(Service, on_delete = models.CASCADE)
    created_at                  = models.DateTimeField(auto_now_add=True)
    updated_at                  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'FavoriteServices'

class Request(models.Model):
    description                 = models.CharField(max_length=200,blank=True)
    client                      = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='client',null=True)
    recipient                   = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='recipient',null=True)
    service                     = models.ForeignKey(Service, on_delete = models.CASCADE,null=True)
    viewed                      = models.BooleanField(blank=True,default=False)

    class Meta:
        verbose_name_plural = 'Requests'
    def  __str__(self):
        return f"{self.service.title}"

class ConcertComplaint(models.Model):
    description                = models.CharField(max_length=600, blank=True)
    owner                      = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='concert_complainant',null=True)
    concert                    = models.ForeignKey(Concert, on_delete = models.CASCADE,null=True)

    class Meta:
        verbose_name_plural = 'Concert Complaints'
    def __str__(self):
        return f"{self.concert.title}"

class ServiceComplaint(models.Model):
    description                = models.CharField(max_length=600, blank=True)
    owner                      = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='service_complainant',null=True)
    service                    = models.ForeignKey(Service,on_delete=models.CASCADE,null=True)

    class Meta:
        verbose_name_plural = 'Service Complaints'
    def __str__(self):
        return f"{self.service.title}"