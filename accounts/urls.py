from django.urls import path
from accounts import views


urlpatterns = [
    path('',views.account,name='account'),
    path('login/',views.login,name='login'),
    path('register/',views.register,name='register'),
    path('logout/',views.logout,name='logout'),
    path('activate/<uidb64>/<token>',views.activate,name='activate'),
    path('reset_password_activate/<uidb64>/<token>',views.reset_password_activate,name='reset_password_activate'),
    path('forget_pass/',views.forget_pass,name='forget_pass'),
    path('reset_pass/',views.reset_pass,name='reset_pass'),
    path('mon_profil/',views.mon_profil,name='mon_profil'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('mes_commandes/',views.mes_commandes,name='mes_commandes'),
    path('mes_transactions/',views.mes_transactions,name='mes_transactions'),
    path('track/<item_id>',views.track,name='track'),
    path('mes_statistiques/',views.mes_statistiques,name='mes_statistiques'),
    path('remboursements/',views.remboursements,name='remboursements'),
    path('parametre/',views.parametre,name='parametre'),
    
    
  
]

