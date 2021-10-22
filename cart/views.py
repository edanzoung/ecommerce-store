from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from cart.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from collections import deque
# Create your views here.
from django.http import HttpResponse, JsonResponse
import json
from django.contrib import messages,auth

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    url = request.META.get('HTTP_REFERER')
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    
    # If the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(variation_category__iexact=key, variation_value__iexact=value, product=product)
                    
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter( product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter( product=product, user=current_user)
            ex_var_list1 = []
            ex_var_list2 = []
            _id1 = []
            _id2 = []

            for item in cart_item:
                existing_variation1 = item.variations.all().order_by('variation_category')
                ex_var_list1.append(list(existing_variation1))
                _id1.append(item.id)
                
            for item in cart_item:
                existing_variation2 = item.variations.all().order_by('variation_category').reverse()
                ex_var_list2.append(list(existing_variation2))
                _id2.append(item.id)
                
            if (product_variation in ex_var_list1):
                # increase the cart item quantity
                index = ex_var_list1.index(product_variation)
                item_id = _id1[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantite += 1
                item.save()
            elif (product_variation in ex_var_list2):
                # increase the cart item quantity
                index = ex_var_list2.index(product_variation)
                item_id = _id2[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantite += 1
                item.save()

            else:

                item = CartItem.objects.create(product=product, quantite=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create( product = product, quantite = 1, user = current_user)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        messages.success(request, str(product.marque_drone)+' '+str(product.modele_drone)+' ajouté au panier !')
        return redirect(url)
    
    # If the user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.all().get(product=product, variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create( cart_id = _cart_id(request))
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing_variations -> database
            # current variation -> product_variation
            # item_id -> database
            ex_var_list1 = []
            ex_var_list2 = []
            _id1 = []
            _id2 = []
            
            for item in cart_item:
                existing_variation1 = item.variations.all().order_by('variation_category')
                ex_var_list1.append(list(existing_variation1))
                _id1.append(item.id)
                
            for item in cart_item:
                existing_variation2 = item.variations.all().order_by('variation_category').reverse()
                ex_var_list2.append(list(existing_variation2))
                _id2.append(item.id)
                
            if (product_variation in ex_var_list1):
                # increase the cart item quantity
                index = ex_var_list1.index(product_variation)
                item_id = _id1[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantite += 1
                item.save()
            elif (product_variation in ex_var_list2):
                # increase the cart item quantity
                index = ex_var_list2.index(product_variation)
                item_id = _id2[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantite += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantite=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create( product=product, quantite=1, cart=cart )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            
        return redirect(url)


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
            
        if cart_item.quantite > 1:
            cart_item.quantite -= 1
            cart_item.save()

    except:
        pass
    return redirect("cart")


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def remove_all(request):
    
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user).delete()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        CartItem.objects.filter(cart=cart).delete()
    return redirect('cart')


def cart(request, total=0, quantite=0, cart_items=None):
    try:
        impot = 0
        grand_total = 0

        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.order_by('product').filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.order_by('product').filter(cart=cart, is_active=True)
            
        for cart_item in cart_items:
            total += (cart_item.product.prix_drone * cart_item.quantite)
            quantite += cart_item.quantite
            
            
        impot = (18 * total)/100
        grand_total = total + impot
        
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total': total,
        'quantite': quantite,
        'cart_items': cart_items,
        'impot'       : impot,
        'grand_total': grand_total,
    }

    return render(request,"shoping-cart.html",context)

def shipping_data(request):
    return render(request,"shipping-data.html")

@login_required(login_url='login')
def checkout(request):
    return render(request,"checkout.html")


