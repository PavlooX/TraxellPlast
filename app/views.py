from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseNotFound
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from .models import *
from .models_local import *
from .serializers import *
from .utils import *
import json


def login_view(request):
    if not request.user.is_authenticated:
        
        # SAFETY CHECKS COMPLETE
        # show login view
        
        return render(request, 'login.html')
    else:
        return redirect('home_view')


def login_account(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            return JsonResponse({'response': 'failed'})

        data = json.loads(request.body)
        email = data['email']
        password = data['password']

        # check if there is user with given email and password
        user = authenticate(email=email, password=password)
        if user:
            # check if account is awaiting approval
            if not user.is_active:
                return JsonResponse({'response': 'awaiting_approval'})

            # SAFETY CHECKS COMPLETE
            # log user in

            login(request, user)
            
            return JsonResponse({'response': 'success'})
        else:
            return JsonResponse({'response': 'failed'})
    else:
        return HttpResponseNotFound()


def logout_account(request):
    if request.user.is_authenticated:
        
        # SAFETY CHECKS COMPLETE
        # log user out and show login view

        logout(request)
        
        return redirect('login_view')


def register_view(request):
    if not request.user.is_authenticated:
        
        # SAFETY CHECKS COMPLETE
        # show register view

        return render(request, 'register.html')
    else:
        return redirect('home_view')


def register_account(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            return JsonResponse({'response': 'failed'})

        data = json.loads(request.body)
        first_name = data['first_name']
        last_name = data['last_name']
        company = data['company']
        email = data['email']
        password = data['password']
        country = data['country']
        address = data['address']
        phone = data['phone']

        # check if all necessary fields are set
        if any(x is None for x in [first_name, last_name, email, password, country, address]):
            return JsonResponse({'response': 'failed'})

        # check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'response': 'failed_email_taken'})

        # SAFETY CHECKS COMPLETE
        # create new user

        User.objects.create(
            first_name = first_name,
            last_name = last_name,
            company = company,
            email = email,
            password = make_password(password),
            country = country,
            address = address,
            phone = phone
        )
        
        return JsonResponse({'response': 'success'})
    else:
        return HttpResponseNotFound()


def home_view(request):
    if request.user.is_authenticated:
        
        # SAFETY CHECKS COMPLETE
        # show home view

        cartbar = Cart.objects.filter(user=request.user).first()
        
        messages = Message.objects.filter(for_admin=True).order_by('-date') if request.user.is_admin else Message.objects.filter(for_user=request.user).order_by('-date')
        
        return render(request, 'home.html', {'user': request.user,
                                             'messages': messages,
                                             'message_choices': MESSAGE_CHOICES,
                                             'cartbar': cartbar})
    else:
        return redirect('login_view')


def account_view(request):
    if request.user.is_authenticated:
        
        # SAFETY CHECKS COMPLETE
        # show account view

        cartbar = Cart.objects.filter(user=request.user).first()
        
        return render(request, 'account.html', {'user': request.user,
                                                'cartbar': cartbar})
    else:
        return redirect('login_view')


def account_save(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({'response': 'failed'})

        data = json.loads(request.body)
        first_name = data['first_name']
        last_name = data['last_name']
        company = data['company']
        email = data['email']
        country = data['country']
        address = data['address']
        phone = data['phone']

        # check if all necessary fields are set
        if any(x is None for x in [first_name, last_name, email, country, address]):
            return JsonResponse({'response': 'failed'})

        # check if user changed email field
        email_changed = True if email != request.user.email else False

        # check if that email is already in use
        if email_changed and User.objects.filter(email=email).exists():
            return JsonResponse({'response': 'failed_email_taken'})

        # SAFETY CHECKS COMPLETE
        # save values to user

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.company = company
        request.user.email = email
        request.user.country = country
        request.user.address = address
        request.user.phone = phone
        request.user.save()
        
        return JsonResponse({'response': 'success_email_changed'}) if email_changed else JsonResponse({'response': 'success'})
    else:
        return HttpResponseNotFound()


def products_view(request):
    if request.user.is_authenticated:
        
        # SAFETY CHECKS COMPLETE
        # show products view

        cartbar = Cart.objects.filter(user=request.user).first()
        
        if request.user.is_admin:
            # admin sees all products
            products = Product.objects.all()
        else:
            # user sees product if it is public or if user is added to products exclucive list
            products = [p for p in Product.objects.all() if p.public or p.exclusive_for.contains(request.user)]
            
        return render(request, 'products.html', {'user': request.user,
                                                 'products': products,
                                                 'cartbar': cartbar})
    else:
        return redirect('login_view')


def product_popup(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({'response': 'failed'})

        data = json.loads(request.body)
        id = data['id']
        model = data['model']

        # find product with given id and model
        product = Product.objects.filter(id=id, model=model).first()
        if not product:
            return JsonResponse({'response': 'failed'})

        # if product is exclusive - check if user is allowed to see the product
        if not product.public and not product.exclusive_for.contains(request.user):
            return JsonResponse({'response': 'failed'})

        # SAFETY CHECKS COMPLETE
        # show product popup

        product_ser = ProductSerializer(product)
        
        return JsonResponse({'response': 'success',
                             'product': product_ser.data})
    else:
        return HttpResponseNotFound()


def item_popup(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({'response': 'failed'})

        data = json.loads(request.body)
        id = data['id']
        model = data['model']

        # find item with given id
        item = Item.objects.filter(id=id).first()
        if not item:
            return JsonResponse({'response': 'failed'})

        # check if item matches product model
        if item.product.model != model:
            return JsonResponse({'response': 'failed'})
        
        # find users cart
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return JsonResponse({'response': 'failed'})

        # check if item is in users cart
        if not cart.items.contains(item):
            return JsonResponse({'response': 'failed'})

        # SAFETY CHECKS COMPLETE
        # show item popup

        item_ser = ItemSerializer(item)
        
        return JsonResponse({'response': 'success',
                             'item': item_ser.data})
    else:
        return HttpResponseNotFound()


def cart_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('home_view')
        else:
            
            # SAFETY CHECKS COMPLETE
            # show cart view

            cart = Cart.objects.filter(user=request.user).first()
            
            return render(request, 'cart.html', {'cart': cart})
    else:
        return redirect('login_view')


def cart_add(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({'response': 'failed'})

        data = json.loads(request.body)
        id = data['id']
        model = data['model']
        mat = data['material']
        color = data['color']
        custom_color = data['custom_color']
        amount = data['amount']
        total_price = data['total_price']

        # find product with given id and model
        product = Product.objects.filter(id=id, model=model).first()
        if not product:
            return JsonResponse({'response': 'failed'})

        # if product is exclusive - check if user is allowed to see the product
        if not product.public and not product.exclusive_for.contains(request.user):
            return JsonResponse({'response': 'failed'})

        # check if amount >= amount_min
        if amount < product.amount_min:
            return JsonResponse({'response': 'failed'})
        
        # find color with given name
        color = product.colors.filter(name=color['name']).first()
        if not color:
            return JsonResponse({'response': 'failed'})

        # find material with given name and price
        material = product.materials.filter(name=mat['name'], price=mat['price']).first()
        if not material:
            return JsonResponse({'response': 'failed'})

        # check if total price is same as calculated
        calc_total_price = amount * material.price
        if total_price != calc_total_price:
            return JsonResponse({'response': 'failed'})

        # SAFETY CHECKS COMPLETE
        # add item to cart

        # find users cart, if there is none create new cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # create new cart item
        new_item = Item(
            product = product,
            material = material,
            color = color,
            amount = amount
        )
        new_item.custom_color = custom_color if color.name == 'custom' else None

        # save new item if - cart is newly created or cart doesnt have same item in items list
        if created or not cart.has_same_item(new_item):
            new_item.save()
            cart.items.add(new_item)

        return JsonResponse({'response': 'success'})
    else:
        return HttpResponseNotFound()


def cart_save(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({'response': 'failed'})

        data = json.loads(request.body)
        id = data['id']
        model = data['model']
        mat = data['material']
        color = data['color']
        custom_color = data['custom_color']
        amount = data['amount']
        total_price = data['total_price']

        # find item with given id
        item = Item.objects.filter(id=id).first()
        if not item:
            return JsonResponse({'response': 'failed'})

        # check if item matches product model
        if item.product.model != model:
            return JsonResponse({'response': 'failed'})
        
        # find users cart
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return JsonResponse({'response': 'failed'})

        # check if item is in users cart
        if not cart.items.contains(item):
            return JsonResponse({'response': 'failed'})

        # check if amount >= amount_min
        if amount < item.product.amount_min:
            return JsonResponse({'response': 'failed'})
        
        # find color with given name
        color = item.product.colors.filter(name=color['name']).first()
        if not color:
            return JsonResponse({'response': 'failed'})

        # find material with given name and price
        material = item.product.materials.filter(name=mat['name'], price=mat['price']).first()
        if not material:
            return JsonResponse({'response': 'failed'})

        # check if total price is same as calculated
        calc_total_price = amount * material.price
        if total_price != calc_total_price:
            return JsonResponse({'response': 'failed'})

        # SAFETY CHECKS COMPLETE
        # save values to item

        item.material = material
        item.color = color
        item.custom_color = custom_color if color.name == 'custom' else None
        item.amount = amount

        # check if item with same specifications already exists
        if cart.has_same_item(item):
            # amount added to existing item - delete this one
            item.delete()
        else:
            # ready to save item
            item.save()

        return JsonResponse({'response': 'success'})
    else:
        return HttpResponseNotFound()

    
def cart_delete(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({'response': 'failed'})

        data = json.loads(request.body)
        id = data['id']
        model = data['model']

        # find item with given id
        item = Item.objects.filter(id=id).first()
        if not item:
            return JsonResponse({'response': 'failed'})

        # check if item matches product model
        if item.product.model != model:
            return JsonResponse({'response': 'failed'})

        # find users cart
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return JsonResponse({'response': 'failed'})

        # check if item is in users cart
        if not cart.items.contains(item):
            return JsonResponse({'response': 'failed'})
        
        # SAFETY CHECKS COMPLETE
        # delete item

        item.delete()

        # if cart is empty - delete cart
        if cart.count_items == 0:
            cart.delete()

        return JsonResponse({'response': 'success'})
    else:
        return HttpResponseNotFound()


def cart_delete_all(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({'response': 'failed'})

        # find users cart
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return JsonResponse({'response': 'failed'})

        # SAFETY CHECKS COMPLETE
        # delete all items inside the cart and then delete the cart
        
        cart.items.all().delete()
        cart.delete()

        return JsonResponse({'response': 'success'})
    else:
        return HttpResponseNotFound()


def cart_submit(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({'response': 'failed'})

        # find users cart
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return JsonResponse({'response': 'failed'})
    
        # SAFETY CHECKS COMPLETE
        # create order

        order = Order.objects.create(user=request.user)

        # add items from cart to order
        order.items.set(cart.items.all())

        # delete users cart
        cart.delete()

        # set items count, amount and price
        order.save()

        # MESSAGE: user - order sent
        Message.objects.create(
            type = MESSAGE_CHOICES[0][0],
            for_user = request.user,
            order = order
        )

        # MESSAGE: admin - order recieved
        Message.objects.create(
            type = MESSAGE_CHOICES[1][0],
            for_admin = True,
            order = order
        )

        return JsonResponse({'response': 'success'})
    else:
        return HttpResponseNotFound()


def orders_view(request):
    if request.user.is_authenticated:
        
        # SAFETY CHECKS COMPLETE
        # show orders view

        cartbar = Cart.objects.filter(user=request.user).first()

        # year
        year_get = request.GET.get('year')
        year = check_year(year_get)

        # sort
        sort_get = request.GET.get('sort')
        if sort_get == ORDER_SORT_CHOICES[0][0]:
            sort = 'price'
        elif sort_get == ORDER_SORT_CHOICES[1][0]:
            sort = '-price'
        elif sort_get == ORDER_SORT_CHOICES[2][0]:
            sort = 'ordered_date'
        elif sort_get == ORDER_SORT_CHOICES[3][0]:
            sort = '-ordered_date'
        else:
            sort_get = ORDER_SORT_CHOICES[3][0]
            sort = '-ordered_date'

        if request.user.is_admin:
            # admin sees all orders
            orders = Order.objects.all().order_by(sort) if year == 'all' else Order.objects.filter(ordered_date__year=year).order_by(sort)
        else:
            # user sees orders he has made
            orders = Order.objects.filter(user=request.user).order_by(sort)

        return render(request, 'orders.html', {'user': request.user,
                                               'orders': orders,
                                               'order_sort_choices': ORDER_SORT_CHOICES,
                                               'order_status_choices': ORDER_STATUS_CHOICES,
                                               'sort': sort_get,
                                               'selected_year': year,
                                               'years': YEARS,
                                               'cartbar': cartbar})
    else:
        return redirect('login_view')
 

# ADMIN
def order_view(request, id):
    if request.user.is_authenticated and request.user.is_admin:
        
        # find order with given id
        order = Order.objects.filter(id=id).first()
        if not order:
            return HttpResponseNotFound()
        
        # SAFETY CHECKS COMPLETE
        # show order view

        return render(request, 'order.html', {'user': request.user,
                                              'order': order,
                                              'order_status_choices': ORDER_STATUS_CHOICES})
    else:
        return HttpResponseNotFound()


# ADMIN
def order_popup(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'response': 'failed'})

        data = json.loads(request.body)
        id = data['id']

        # find order with given id
        order = Order.objects.filter(id=id).first()
        if not order:
            return JsonResponse({'response': 'failed'})
      
        # SAFETY CHECKS COMPLETE
        # show order popup

        order_ser = OrderSerializer(order)
        
        return JsonResponse({'response': 'success',
                             'order': order_ser.data,
                             'order_status_choices': ORDER_STATUS_CHOICES})
    else:
        return HttpResponseNotFound()


# ADMIN
def order_save(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'response': 'failed'})

        data = json.loads(request.body)
        id = data['id']
        order_status = data['order_status']
        in_process_date = data['in_process_date']
        shipped_date = data['shipped_date']

        # find order with given id
        order = Order.objects.filter(id=id).first()
        if not order:
            return JsonResponse({'response': 'failed'})

        # check if order status value exists in choices list
        if not any(x[0] == order_status for x in ORDER_STATUS_CHOICES):
            return JsonResponse({'response': 'failed'})

        # check date format for in process
        if not is_date_format(in_process_date):
            in_process_date = None

        # check date format for shipped
        if not is_date_format(shipped_date):
            shipped_date = None

        # SAFETY CHECKS COMPLETE
        # save order values

        old_order_status = order.order_status
        order.order_status = order_status
        order.in_process_date = in_process_date
        order.shipped_date = shipped_date

        order.save(update_fields=['order_status', 'in_process_date', 'shipped_date'])

        # MESSAGE: admin and user - order status updated
        if old_order_status != order_status:
            Message.objects.create(
                type = MESSAGE_CHOICES[2][0],
                for_admin = True,
                for_user = order.user,
                order = order
            )

        return JsonResponse({'response': 'success'})
    else:
        return HttpResponseNotFound()


# ADMIN
def users_view(request):
    if request.user.is_authenticated and request.user.is_admin:
        
        # SAFETY CHECKS COMPLETE
        # show users view - all active users except admins
        
        # year
        year_get = request.GET.get('year')
        year = check_year(year_get)

        # sort
        sort_get = request.GET.get('sort')
        if sort_get == USER_SORT_CHOICES[0][0]:
            users = sorted(User.objects.filter(is_active=True, is_admin=False), key=lambda u:u.count_orders(year))
        elif sort_get == USER_SORT_CHOICES[1][0]:
            users = sorted(User.objects.filter(is_active=True, is_admin=False), key=lambda u:u.count_orders(year), reverse=True)
        elif sort_get == USER_SORT_CHOICES[2][0]:
            users = sorted(User.objects.filter(is_active=True, is_admin=False), key=lambda u:u.orders_total_price(year))
        elif sort_get == USER_SORT_CHOICES[3][0]:
            users = sorted(User.objects.filter(is_active=True, is_admin=False), key=lambda u:u.orders_total_price(year), reverse=True)
        else:
            sort_get = USER_SORT_CHOICES[3][0]
            users = sorted(User.objects.filter(is_active=True, is_admin=False), key=lambda u:u.orders_total_price(year), reverse=True)

        return render(request, 'users.html', {'users': users,
                                              'user_sort_choices': USER_SORT_CHOICES,
                                              'sort': sort_get,
                                              'selected_year': year,
                                              'years': YEARS})
    else:
        return HttpResponseNotFound()


# ADMIN
def user_view(request, id):
    if request.user.is_authenticated and request.user.is_admin:
        
        # find user with given id
        user_requested = User.objects.filter(id=id).first()
        if not user_requested:
            return HttpResponseNotFound()

        # SAFETY CHECKS COMPLETE
        # show user view

        # year
        year_get = request.GET.get('year')
        year = check_year(year_get)

        return render(request, 'user.html', {'user': user_requested,
                                             'selected_year': year})
    else:
        return HttpResponseNotFound()


# ADMIN
def user_analysis_view(request, id):
    if request.user.is_authenticated and request.user.is_admin:

        # find user with given id
        user_requested = User.objects.filter(id=id).first()
        if not user_requested:
            return HttpResponseNotFound()

        # year
        year_get = request.GET.get('year')
        year = check_year(year_get)

        # check if orders count is more than 0
        if user_requested.count_orders(year) == 0:
            return HttpResponseNotFound()

        # SAFETY CHECKS COMPLETE
        # show user analysis view

        return render(request, 'user_analysis.html', {'user': user_requested,
                                                      'selected_year': year})
    else:
        return HttpResponseNotFound()


# ADMIN
def financy_view(request):
    if request.user.is_authenticated and request.user.is_admin:
        
        # SAFETY CHECKS COMPLETE
        # show financy view - analysis for orders, products, most expensive, cheapest

        # year
        year_get = request.GET.get('year')
        year = check_year(year_get)

        financy = FinancyLocal(year)
        
        return render(request, 'financy.html', {'data': financy,
                                                'selected_year': year,
                                                'years': YEARS})
    else:
        return HttpResponseNotFound()