
from store.models import Product,Variation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def Drone_id(request):
    drone=0
    products = Product.objects.all()
    for data in products:
        drone = data.id

    drone_variation_color = Variation.objects.all()
    
    return dict(products = products,drone = drone)