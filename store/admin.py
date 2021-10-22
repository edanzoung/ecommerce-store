from django.contrib import admin
from store.models import Product, Variation, ReviewRating
    
class ProductAdmin(admin.ModelAdmin):
    list_display=("marque_drone","modele_drone","categorie_drone","quantite_drone","prix_drone","date_modification","availability",)
    list_display_links=("marque_drone","modele_drone",)
    ordering=("-date_creation",)
    search_fields=("marque_drone","modele_drone","categorie_drone","quantite_drone","prix_drone","date_modification","availability",)
    prepopulated_fields={'slug':("modele_drone",)}
    filter_horizontal=()
    list_filter=()
    fieldsets=()
    
class VariationAdmin(admin.ModelAdmin):
    list_display=("product","variation_category","variation_value","is_active",)
    list_display_links=("product","variation_category",)
    list_editable=("is_active",)
    ordering=("-date_creation",)
    search_fields=("product","variation_category","variation_value","is_active",)
    filter_horizontal=()
    list_filter=()
    fieldsets=()
    
admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)