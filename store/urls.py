from django.urls import path
from store import views


urlpatterns = [
    
    path('',views.product,name='product'),
    path('category/<slug:category_slug>/',views.product,name='products_by_category'),
    path('category/product_detail/<product_id>/',views.product_detail,name='product_detail'),
    path('search/',views.product,name='search'),
    path('submit_review/<int:item_id>/', views.submit_review, name='submit_review'),
    
]

