from django.shortcuts import render,redirect, get_object_or_404
from django.db.models import Q
from store.models import Product, Variation, ReviewRating
from category.models import Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse,Http404
from django.contrib.auth.decorators import login_required
#from django.template import loader
# Create your views here.

from store.forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

def home(request):
    return render(request,"index.html")

def contact(request):
    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")

def blog(request):
    return render(request,"blog.html")

def blog_detail(request):
    return render(request,"blog-detail.html")

def handler404(request,exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)


def product(request,category_slug=None):
    
    categories=None
    product_list = None
    
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword is not None:
            product_list = Product.objects.order_by('date_creation').filter(
                Q(marque_drone__icontains=keyword) | Q(modele_drone__icontains=keyword) ).distinct()
        
    elif category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        product_list = Product.objects.filter(categorie_drone=categories,availability=True)
    else:
        product_list = Product.objects.all().filter(availability=True).order_by('date_creation')

    paginator = Paginator(product_list,8) # Show 8 drones per page. 
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    precedent_num1=int(page_obj.number)-3
    precedent_num2=int(page_obj.number)-2
    precedent_num3=int(page_obj.number)-1
    
    suivant_num1=int(page_obj.number)+1
    suivant_num2=int(page_obj.number)+2
    suivant_num3=int(page_obj.number)+3

    context = {'drones' : product_list,'list_drone_size':int(len(product_list)),
                'page_obj': page_obj,'page_total':page_obj.paginator.num_pages,
               'precedent_num1':precedent_num1,'suivant_num1':suivant_num1,
              'precedent_num2':precedent_num2,'suivant_num2':suivant_num2,
              'precedent_num3':precedent_num3,'suivant_num3':suivant_num3}
    
    return render(request,"product.html",context)


def product_detail(request,product_id):
    try:
        drone_id=Product.objects.get(id=product_id)
    except Exception as e:
        raise e
        
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=drone_id.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=drone_id.id, status=True)
    
    context = {
        'drone':drone_id,
        'orderproduct': orderproduct,
        'reviews': reviews,

    }
    
    return render(request,"product-detail.html",context)

@login_required(login_url='login')
def submit_review(request, item_id):
    url = request.META.get('HTTP_REFERER')
    
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user_id=request.user.id, product_id=item_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            #print('url',url)
            #messages.success(request, 'Merci votre review a été mise à jour')
            
            #return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = item_id
                data.user_id = request.user.id
                data.save()
                #messages.success(request, 'Merci votre review a été soumis')
                
    return redirect(url)