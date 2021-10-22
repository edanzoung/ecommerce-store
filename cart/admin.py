from django.contrib import admin
from cart.models import Cart, CartItem

# Register your models here.
class CartAdmin_Cart(admin.ModelAdmin):
    list_display=("cart_id","date_added",)
    #list_display_links=("cart_id","product",)
    search_fields=("cart_id","date_added",)
    filter_horizontal=()
    list_filter=()
    fieldsets=()

class CartAdmin_CartItem(admin.ModelAdmin):
    list_display=("product","cart","quantite","is_active",)
    list_display_links=("product",)
    search_fields=("product","cart","quantite","is_active",)
    filter_horizontal=()
    list_filter=()
    fieldsets=()
    
admin.site.register(Cart,CartAdmin_Cart)

admin.site.register(CartItem,CartAdmin_CartItem)