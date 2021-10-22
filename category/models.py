from django.db import models
from django.urls import reverse
from category.storage import OverwriteStorage
custom_store = OverwriteStorage()

# Create your models here.
class Category(models.Model):
    
    category_name = models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    description = models.TextField(max_length=200,blank=True)
    cat_image = models.ImageField(storage=custom_store,upload_to='media/categories/',blank=True)
    
    class Meta:
        verbose_name="Category"
        verbose_name_plural="Categories"
        
    def get_url(self):
        return reverse('products_by_category',args=[self.slug])
    
    def __str__(self):
        return '{0} {1}'.format(self.category_name,self.slug)
