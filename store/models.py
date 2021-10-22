from django.db import models
from category.models import Category
from store.storage import OverwriteStorage

from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count

custom_store = OverwriteStorage()


# Create your models here.
class Product(models.Model):
    MARQUE = (
        ('N/A', 'N/A'),
        ('3D-ROBOTICS', '3D-ROBOTICS'),       
        ('AERYON', 'AERYON'),
        ('AEE-TECHNOLOGY', 'AEE-TECHNOLOGY'),
        ('AIRWARE', 'AIRWARE'),
        ('ASCENDING-TECHNOLOGIES', 'ASCENDING-TECHNOLOGIES'),
        ('AUTEL', 'AUTEL'),      
        ('CYPHY', 'CYPHY'),
        ('CYBAERO', 'CYBAERO'),
        ('DJI', 'DJI'),
        ('DROCON', 'DROCON'),
        ('EACHINE', 'EACHINE'),
        ('EHANG', 'ALVIS'),
        ('HUBSAN', 'HUBSAN'),
        ('INSITU', 'INSITU'),
        ('MAPBOX', 'MAPBOX'),
        ('PARROT', 'PARROT'),
        ('PIX4D', 'PIX4D'),
        ('POTENSIC', 'POTENSIC'),
        ('PRECISIONHAWK', 'PRECISIONHAWK'),   
        ('SABRE', 'SABRE'),
        ('SENSEFLY', 'SENSEFLY'),
        ('SKYCATCH', 'SKYCATCH'),
        ('SNAPTAIN', 'SNAPTAIN'),
        ('SQHADRONE-SYSTEM', 'SQHADRONE-SYSTEM'), 
        ('SYMA', 'SYMA'),
        ('TOMZON', 'TOMZON'),
        ('WALKERA', 'WALKERA'), 
        ('XIRO', 'XIRO'),
        ('YUNEEC', 'YUNEEC'))
        

    ETAT = (
        ('N/A', 'N/A'),
        ('NEUF', 'NEUF'),
        ('SECONDE-MAIN', 'SECONDE-MAIN'))
    
    categorie_drone = models.ForeignKey(Category,on_delete=models.CASCADE)
    
    marque_drone = models.CharField(max_length=100,choices=MARQUE,blank=True)
    modele_drone = models.CharField(max_length=200,unique=True)
    
    slug = models.SlugField(max_length=200,unique=True)
    
    annee_drone = models.IntegerField(default=0)
    
    etat_drone = models.CharField(max_length=100,choices=ETAT,blank=True)
    autonomie_drone = models.IntegerField(default=0)
    distance_drone = models.IntegerField(default=0)
    vitesse_drone = models.IntegerField(default=0)
    
    poids_drone = models.IntegerField(default=0)
    
    description_drone = models.TextField(max_length=200,blank=True)
    
    quantite_drone = models.IntegerField(default=0)
    prix_drone = models.IntegerField(default=0)
    
    availability = models.BooleanField(default=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    image1_drone = models.ImageField(storage=custom_store,upload_to='static/images/drones/', max_length=255)
    image2_drone = models.ImageField(storage=custom_store,upload_to='static/images/drones/', max_length=255)
    image3_drone = models.ImageField(storage=custom_store,upload_to='static/images/drones/', max_length=255)
    image4_drone = models.ImageField(storage=custom_store,upload_to='static/images/drones/', max_length=255)
    image5_drone = models.ImageField(storage=custom_store,upload_to='static/images/drones/', max_length=255)
       
    
    class Meta:
        verbose_name="Product"
        verbose_name_plural="Products"
    
    def __str__(self):
        return '{0} {1}'.format(self.marque_drone,self.modele_drone)
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
    
class VariationManager(models.Manager):
    def offers(self):
        return super(VariationManager, self).filter(variation_category="offre", is_active=True)
    def colors(self):
        return super(VariationManager, self).filter(variation_category="couleur", is_active=True)
    
    
    
variation_category_choice = (
    ('offre','offre'), 
    ('couleur','couleur'),
        
    )
    
class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=200,choices=variation_category_choice)
    variation_value = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()
    
    class Meta:
        ordering = ('variation_category',)

    def __str__(self):
        return self.variation_value
    
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject