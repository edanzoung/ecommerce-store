from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager
# Create your models here.
from accounts.storage import OverwriteStorage
custom_store = OverwriteStorage()

class MyAccountManager(BaseUserManager):
    
    def create_user(self,first_name,last_name,username,email,gender,country,state,city,quartier,password=None):
        if not email:
            raise ValueError("L'utilisateur doit avoir un email")
            
        if not username:
            raise ValueError("L'utilisateur doit avoir un username")
            
        user=self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            country=country,
            state=state,
            city=city,
            quartier=quartier,
        )   
        user.set_password(password)
        user.save(using=self._db)
        
        return user
        
    def create_superuser(self,first_name,last_name,username,email,gender,country,state,city,quartier,password): 
        
        user=self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,   
            gender=gender,
            country=country,
            state=state,
            city=city,
            quartier=quartier,
        )   
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superadmin = True
        user.save(using=self._db)
        
        return user

class Account(AbstractBaseUser):
    
    GENDER = (
        ('M', 'M'),
        ('F', 'F'))
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=100,unique=True)
    phone_number = models.CharField(max_length=50,blank=True)
    gender = models.CharField(max_length=50,choices=GENDER,blank=True)
    country = models.CharField(max_length=50,blank=True)
    state = models.CharField(max_length=50,blank=True)
    city = models.CharField(max_length=50,blank=True)
    quartier = models.CharField(max_length=50,blank=True)
    
    # Required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','username','gender','country','state','city','quartier']
    
    objects = MyAccountManager()
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
    
class UserProfile(models.Model):
    
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    profile_picture = models.ImageField(storage=custom_store,upload_to='media/profile/', max_length=255)
    gender = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)
    city = models.CharField(blank=True, max_length=20)
    quartier = models.CharField(blank=True, max_length=20)
    

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
