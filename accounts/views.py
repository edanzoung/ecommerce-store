from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse,Http404
from accounts.forms import RegistrationForm, UserForm, UserProfileForm
from accounts.models import Account,UserProfile
from orders.models import Order, OrderProduct,Payment
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required

#User Activation
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist

from cart.views import _cart_id
from cart.models import Cart, CartItem
from django.contrib.auth.models import AnonymousUser
# Create your views here.

def register(request): 
    form = RegistrationForm(request.POST)
    
    if form.is_valid():
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']            
        phone_number = form.cleaned_data['phone_number']
        password = form.cleaned_data['password']
        username = email.split('@')[0]
        gender = form.cleaned_data['gender']            
        country = form.cleaned_data['country']
        state = form.cleaned_data['state']
        city = form.cleaned_data['city']
        quartier = form.cleaned_data['quartier']
        
        user = Account.objects.create_user(first_name=first_name, last_name=last_name,
                                           username=username, email=email, password=password,gender=gender,
                                          country=country,state=state,
                                          city=city,quartier=quartier)
        user.phone_number = phone_number
        user.save()
        
        #User Activation
        current_site=get_current_site(request)
        mail_subject = 'FasoDrone Compte Activation'
        message=render_to_string('account-verification.html',{
            
            'user':user,
            'domain':current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user),            
        })
        to_email=email
        send_email=EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()
        
        messages.success(request,"Merci d'avoir effectué une inscription sur FasoDrone. Un email a été envoyé à votre adresse email pour vérification . Veuillez véifier s'il vous plaît ")
        
        return redirect('/accounts/login/?command=verification&email='+email)
        
    else:
        #messages.success(request,'Inscription échouée')
        form = RegistrationForm()
    
    context = {'form' : form}
    return render(request,"register.html",context)


def login(request):
    
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        
        user= auth.authenticate(email=email,password=password)
        
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item1 = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item1:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_item2 = CartItem.objects.filter(user=user)
                    ex_var_list1 = []
                    _id1 = []
                    
                    for item in cart_item2:
                        existing_variation1 = item.variations.all().order_by('variation_category')
                        ex_var_list1.append(list(existing_variation1))
                        _id1.append(item.id)
                        
                    cart_item3 = CartItem.objects.filter(user=user)
                    ex_var_list2 = []
                    _id2 = []
                        
                    for item in cart_item3:
                        existing_variation2 = item.variations.all().order_by('variation_category').reverse()
                        ex_var_list2.append(list(existing_variation2))
                        _id2.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list1:
                            index = ex_var_list1.index(pr)
                            item_id = _id1[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantite += 1
                            item.user = user
                            item.save()
                        elif pr in ex_var_list2:
                            index = ex_var_list2.index(pr)
                            item_id = _id2[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantite += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
                    
            except :
                pass
            
            auth.login(request,user)
            #messages.success(request,'Compte connecté avec succès')
            
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                #print('query ==>',query)
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                #print('params ==>',params)
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except :
                return redirect('account')
            
        else:
            #messages.warning(request,'Connexion échouée')
            return redirect('login')
    
    return render(request,"login.html")



@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    #messages.success(request,'Compte déconnecté avec succès')
    return redirect('login')


def forget_pass(request):
    
    if request.method=='POST':
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user= Account.objects.get(email__exact=email)
            
            #Reset Password
            current_site=get_current_site(request)
            mail_subject = 'Cozastore Réinitialisation Mot De Passe'
            message=render_to_string('reset-password-verification.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user), 
            })
            to_email=email
            send_email=EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request,"""Un email de réinitialisation de mot de passe a été envoyé à votre adresse email. Veuillez véifier s'il vous plaît """)
            return redirect('login')
        else:
            messages.warning(request,"""Ce compte n'existe pas dans notre bases de donnée""")
            return redirect('forget_pass')
            
    return render(request,"forget-pass.html")


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user= Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverFlowError,Account.DoesNotExit):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Félicitation! Votre compte est activé')
        return redirect('login')
    else:
        messages.warning(request, "Lien d'activation expiré")
        return redirect('register')
    
def reset_password_activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user= Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverFlowError,Account.DoesNotExit):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['id'] = uid
        messages.success(request, 'Veuillez saisir un nouveau mot de passe')
        return redirect('reset_pass')
    else:
        messages.warning(request, "Lien de réinitialisation expiré")
        return redirect('login')
    
def reset_pass(request):
    
    if request.method=='POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        
        if password == confirm_password:
            uid=request.session.get('id')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Mot de passe réinitialisé avec succès')
            return redirect('login')
        else:
            messages.success(request, 'Mot de passe non identique')
            return redirect('reset_pass')
            
    return render(request,"reset-pass.html")
    

# Account Pages
@login_required(login_url='login')
def account(request):
    orders_count=0
    userprofile=None
    grand_total_order=0
    try:
        orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
        orders_count = orders.count()
        
        for order in orders:
            grand_total_order += order.order_total

        userprofile = UserProfile.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        pass
    
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
        'grand_total_order': grand_total_order,
    }
    return render(request,"account.html",context)


def mon_profil(request):
    return render(request,"mon-profil.html")


def track(request,item_id):
    track_item = Order.objects.get(order_number=item_id)
    #print(track_item.last_name)
    context = {
        'track_item': track_item,
        }
    return render(request,"track-shipping.html", context)


def mes_commandes(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    grand_total_order=0
    
    for order in orders:
        grand_total_order += order.order_total
    
    
    context = {
        'orders': orders,
        'grand_total_order': grand_total_order,
        }
    return render(request,"mes-commandes.html", context)


def mes_transactions(request):
    grand_total_order=0
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    for payment in payments:
        grand_total_order += float(payment.amount_paid)
    
    
    context = {
        'payments': payments,
        'grand_total_order': grand_total_order,
        }
    return render(request,"mes-transactions.html",context)


def mes_statistiques(request):
    orders_count=0
    userprofile=None
    grand_total_order=0
    try:
        orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
        orders_count = orders.count()   
        
        for order in orders:
            grand_total_order += order.order_total

        userprofile = UserProfile.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        pass
    
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
        'grand_total_order': grand_total_order,
    }
    return render(request,"mes-statistiques.html",context)


def remboursements(request):
    return render(request,"remboursements.html")


def parametre(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    user_form = UserForm(instance=request.user)
    profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'parametre.html',context)


def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Votre profile a été mise à jour')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'parametre.html',context)


def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password and new_password != '' and confirm_password != '':
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Mot de passe mise à jour.')
                return redirect('login')
            else:
                messages.success(request, 'Changement non effectué')
                return redirect('parametre')
        else:
            messages.success(request, 'Changement non effectué')
            return redirect('parametre')
    return render(request, 'parametre.html')