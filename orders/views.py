from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from cart.models import CartItem
from orders.forms import OrderForm
import datetime
from orders.models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantite
        orderproduct.product_price = item.product.prix_drone
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.quantite_drone -= item.quantite
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Merci pour votre commande !'
    message = render_to_string('order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = 'elkanazoungrana@gmail.com' #request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def place_order(request, total=0, quantite=0):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)

    grand_total = 0
    impot = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.prix_drone * cart_item.quantite)
        quantite += cart_item.quantite
        
    impot = (18 * total)/100
    grand_total = total + impot
    
    impot_usd = '%.2f'%float(impot/558)
    total_usd = '%.2f'%float(total/558)
    grand_total_usd = '%.2f'%float(grand_total/558)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.quartier = form.cleaned_data['quartier']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = impot
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            now = datetime.datetime.now()
            current_date = now.strftime("%Y%m%d") #20210305
            print('current_date',current_date)
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'impot': impot,
                'grand_total': grand_total,
                'impot_usd': impot_usd,
                'total_usd': total_usd,
                'grand_total_usd': grand_total_usd,
            }
            
            return render(request, 'paiement.html', context)
    
    else:
        return render('shipping_data')
    


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('index')

