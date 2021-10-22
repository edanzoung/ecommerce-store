from category.models import Category
from cart.models import Cart, CartItem
from cart.views import _cart_id

def counter(request):
    cart_count=0
    cart_items=None
    quantite=0
    total=0
    impot=0
    grand_total=0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().order_by('product').filter(user=request.user)
            else:
                
                cart_items = CartItem.objects.all().order_by('product').filter(cart=cart[:1])
                
            for cart_item in cart_items:
                cart_count += cart_item.quantite
                quantite += cart_item.quantite
                total += (cart_item.product.prix_drone * cart_item.quantite)
                impot = (total*18)/100
                grand_total = total + impot
                
        except Cart.DoesNotExist:
            cart_count = 0
            
    return dict(cart_count=cart_count,overview_cart_items=cart_items,
                quantite=quantite,total=total,
               impot=impot,grand_total=grand_total)