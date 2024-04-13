from django import template
from django.urls import reverse
from app.models import ORDER_STATUS_CHOICES, ORDER_SORT_DEFAULT, USER_SORT_DEFAULT
from app.utils import *

register = template.Library()


@register.filter
def year_format(value):
    return '[{}.]'.format(value) if type(value) == int else None

@register.filter
def order_format(value):
    return 'ORDER #{}'.format(value)

@register.filter
def sequence(value, counter):
    return '{}. {}'.format(counter, value)

@register.filter
def euro(value):
    return '{} \u20ac'.format(value)

@register.filter
def status_date(value, order):
    if order.order_status == ORDER_STATUS_CHOICES[2][0]:
        if order.in_process_date:
            return '{} ({})'.format(value, order.in_process_date.strftime('%#d.%#m.%Y.'))
    elif order.order_status == ORDER_STATUS_CHOICES[3][0]:
        if order.shipped_date:
            return '{} ({})'.format(value, order.shipped_date.strftime('%#d.%#m.%Y.'))
    return value


@register.simple_tag
def user_orders(user, year):
    return user.orders(year)

@register.simple_tag
def user_count_orders(user, year):
    return user.count_orders(year)

@register.simple_tag
def user_orders_total_price(user, year):
    return user.orders_total_price(year)

@register.simple_tag
def user_orders_by_months(user, year):
    return user.orders_by_months(year)

@register.simple_tag
def user_items(user, year):
    return user.items(year)

@register.simple_tag
def url_parameters(value, year=None):
    return '{}?year={}'.format(value, year)


@register.inclusion_tag('arrow.html')
def arrow(id):
    return {'id': id}

@register.inclusion_tag('model_viewer.html')
def model_viewer(source):
    return {'source': source}

@register.inclusion_tag('navbar_page.html')
def navbar_page(page, current_page, admin=False):
    if page == 'login':
        title = 'LOG IN'
        image = '/static/images/login.png'
        url = reverse('login_view')
        selected = True if current_page == 'login' else False

    elif page == 'register':
        title = 'REGISTER'
        image = '/static/images/register.png'
        url = reverse('register_view')
        selected = True if current_page == 'register' else False

    elif page == 'account':
        title = 'ACCOUNT'
        image = '/static/images/profile.png'
        url = reverse('account_view')
        selected = True if current_page == 'account' else False

    elif page == 'products':
        title = 'PRODUCTS'
        image = '/static/images/products.png'
        url = reverse('products_view')
        selected = True if current_page == 'products' else False

    elif page == 'cart':
        title = 'CART'
        image = '/static/images/cart.png'
        url = reverse('cart_view')
        selected = True if current_page == 'cart' else False

    elif page == 'orders':
        title = 'ORDERS'
        image = '/static/images/orders.png'
        url = '{}?sort={}&year={}'.format(reverse('orders_view'), ORDER_SORT_DEFAULT, current_year()) if admin else '{}?sort={}'.format(reverse('orders_view'), ORDER_SORT_DEFAULT)
        selected = True if current_page == 'orders' else False

    elif page == 'users':
        title = 'USERS'
        image = '/static/images/users.png'
        url = '{}?sort={}&year={}'.format(reverse('users_view'), USER_SORT_DEFAULT, current_year())
        selected = True if current_page == 'users' else False

    elif page == 'financy':
        title = 'FINANCY'
        image = '/static/images/financy.png'
        url = '{}?year={}'.format(reverse('financy_view'), current_year())
        selected = True if current_page == 'financy' else False

    elif page == 'logout':
        title = 'LOG OUT'
        image = '/static/images/logout.png'
        url = reverse('logout_account')
        selected = True if current_page == 'logout' else False

    return {'title': title,
            'image': image,
            'url': url,
            'selected': selected}

@register.inclusion_tag('header.html')
def header(title, subtitle=None, right=None, right_url=None, url_open_type=None, image=None):
    if right == 'edit':
        image = '/static/images/edit.png'
        url_open_type = 'current_page'

    elif right == 'analyze':
        image = '/static/images/financy.png'
        url_open_type = 'new_page'

    return {'title': title,
            'subtitle': subtitle,
            'right': right,
            'right_url': right_url,
            'url_open_type': url_open_type,
            'image': image}

@register.inclusion_tag('group.html')
def group(type, title=None, content=None, content_bold=None, context=None, more=None, last=False):
    if type == 'customer':
        title = 'CUSTOMER'
        image = '/static/images/profile.png'

    elif type == 'email':
        title = 'EMAIL'
        image = '/static/images/messages.png'

    elif type == 'location':
        title = 'LOCATION'
        image = '/static/images/location.png'

    elif type == 'phone':
        title = 'PHONE NUMBER'
        image = '/static/images/phone.png'

    elif type == 'messages':
        title = 'MESSAGES'
        image = '/static/images/messages.png'

    elif type == 'orders':
        title = 'ORDERS'
        image = '/static/images/orders.png'

    elif type == 'products':
        title = 'PRODUCTS'
        image = '/static/images/products.png'

    elif type == 'items':
        title = 'ITEMS'
        image = '/static/images/items.png'

    elif type == 'material':
        title = 'MATERIAL'
        image = '/static/images/material.png'

    elif type == 'color':
        title = 'COLOR'
        image = '/static/images/color.png'

    elif type == 'status':
        title = 'STATUS'
        image = '/static/images/status.png'

    elif type == 'status_date':
        title = context.order_status_display
        image = context.order_status_image

    elif type == 'months':
        image = '/static/images/date.png'

    elif type == 'amount':
        title = 'AMOUNT'
        image = '/static/images/amount.png'

    elif type == 'price':
        title = 'TOTAL PRICE'
        image = '/static/images/price.png'

    elif type == 'price_detailed':
        title = 'TOTAL PRICE'
        image = '/static/images/price.png'
        content = '{:,} * {} \u20ac'.format(context.amount, context.material.price)

    return {'title': title,
            'image': image,
            'content': content,
            'content_bold': content_bold,
            'more': more,
            'last': last}

@register.inclusion_tag('group_product.html')
def group_product(type, title=None, title_only=False, content=None, last=False):
    if type == 'product_public':
        title = 'PRODUCT PUBLIC'
        title_only = True
        image = '/static/images/public.png'

    elif type == 'product_exclusive':
        title = 'PRODUCT AVAILABLE FROM EXAMPLE'
        image = '/static/images/info.png'
        content = 'www.example.com'

    return {'title': title,
            'title_only': title_only,
            'image': image,
            'content': content,
            'last': last}

@register.inclusion_tag('group_list_all.html')
def group_list_all(type, title=None, content=None, last=False):
    if type == 'material':
        title = 'MATERIAL'
        image = '/static/images/material.png'
        lst = [x.get_name_display for x in content]
        content = lst

    elif type == 'price':
        title = 'PRICE'
        image = '/static/images/price.png'
        lst = ['{} \u20ac / per piece'.format(x.price) for x in content]
        content = lst

    elif type == 'color':
        title = 'COLOR'
        image = '/static/images/color.png'
        lst = [x.get_name_display for x in content]
        content = lst

    elif type == 'product_exclusive':
        title = 'PRODUCT EXCLUSIVE'
        image = '/static/images/profile.png'
        lst = [x.full_name for x in content]
        content = lst

    return {'title': title,
            'image': image,
            'content': content,
            'last': last}

@register.inclusion_tag('group_files.html')
def group_files(type, content=None, context=None, last=False):
    if type == 'product':
        lst = [('DOCUMENTATION', 'url'), ('3D MODEL', 'url')]
        content = lst

    return {'content': content,
            'last': last}


class Input:
    def __init__(self, type=None, id=None, title=None, value=None, placeholder=None, onchange=None):
        self.type = type
        self.id = id
        self.title = title
        self.value = value
        self.placeholder = placeholder
        self.onchange = onchange

@register.inclusion_tag('group_input.html')
def group_input(type, context=None, last=False):
    inputs = []

    if type == 'customer_reg':
        image = '/static/images/profile.png'
        image_id = 'customer_image'
        inputs.extend([
            Input(
                type = 'text',
                id = 'first_name_input',
                title = 'FIRST NAME *',
                placeholder = 'Enter first name',
                onchange = 'checkRegister()'
            ),
            Input(
                type = 'text',
                id = 'last_name_input',
                title = 'LAST NAME *',
                placeholder = 'Enter last name',
                onchange = 'checkRegister()'
            ),
            Input(
                type = 'text',
                id = 'company_input',
                title = 'COMPANY',
                placeholder = 'Enter company'
            )
        ])
    elif type == 'customer_edit':
        image = '/static/images/profile.png'
        image_id = 'customer_image'
        inputs.extend([
            Input(
                type = 'text',
                id = 'first_name_input',
                title = 'FIRST NAME *',
                value = context.first_name,
                placeholder = 'Enter first name',
                onchange = 'checkSave()'
            ),
            Input(
                type = 'text',
                id = 'last_name_input',
                title = 'LAST NAME *',
                value = context.last_name,
                placeholder = 'Enter last name',
                onchange = 'checkSave()'
            ),
            Input(
                type = 'text',
                id = 'company_input',
                title = 'COMPANY',
                value = context.company,
                placeholder = 'Enter company'
            )
        ])

    elif type == 'email_reg':
        image = '/static/images/messages.png'
        image_id = 'email_image'
        inputs.append(Input(
            type = 'email',
            id = 'email_input',
            title = 'EMAIL *',
            placeholder = 'Enter email',
            onchange = 'checkRegister()'
        ))
    elif type == 'email_login':
        image = '/static/images/messages.png'
        image_id = 'email_image'
        inputs.append(Input(
            type = 'email',
            id = 'email_input',
            title = 'EMAIL',
            placeholder = 'Enter email',
            onchange = 'checkLogin()'
        ))
    elif type == 'email_edit':
        image = '/static/images/messages.png'
        image_id = 'email_image'
        inputs.append(Input(
            type = 'email',
            id = 'email_input',
            title = 'EMAIL *',
            value = context.email,
            placeholder = 'Enter email',
            onchange = 'checkSave()'
        ))

    elif type == 'location_reg':
        image = '/static/images/location.png'
        image_id = 'location_image'
        inputs.extend([
            Input(
                type = 'text',
                id = 'country_input',
                title = 'COUNTRY *',
                placeholder = 'Enter country',
                onchange = 'checkRegister()'
            ),
            Input(
                type = 'text',
                id = 'address_input',
                title = 'ADDRESS *',
                placeholder = 'Enter address',
                onchange = 'checkRegister()'
            )
        ])
    elif type == 'location_edit':
        image = '/static/images/location.png'
        image_id = 'location_image'
        inputs.extend([
            Input(
                type = 'text',
                id = 'country_input',
                title = 'COUNTRY *',
                value = context.country,
                placeholder = 'Enter country',
                onchange = 'checkSave()'
            ),
            Input(
                type = 'text',
                id = 'address_input',
                title = 'ADDRESS *',
                value = context.address,
                placeholder = 'Enter address',
                onchange = 'checkSave()'
            )
        ])

    elif type == 'phone_reg':
        image = '/static/images/phone.png'
        image_id = 'phone_image'
        inputs.append(Input(
            type = 'tel',
            id = 'phone_input',
            title = 'PHONE NUMBER',
            placeholder = '+xxx 12 345 6789'
        ))
    elif type == 'phone_edit':
        image = '/static/images/phone.png'
        image_id = 'phone_image'
        inputs.append(Input(
            type = 'tel',
            id = 'phone_input',
            title = 'PHONE NUMBER',
            value = context.phone,
            placeholder = '+xxx 12 345 6789'
        ))

    return {'image': image,
            'image_id': image_id,
            'inputs': inputs,
            'last': last}

@register.inclusion_tag('group_input_password.html')
def group_input_password(type, context=None, last=False):
    if type == 'password_reg':
        image = '/static/images/password.png'
        image_id = 'password_image'
        input = Input(type = 'password',
                      id = 'password_input',
                      title = 'PASSWORD *',
                      placeholder = 'Enter password',
                      onchange = 'checkRegister()')
        
    elif type == 'password_login':
        image = '/static/images/password.png'
        image_id = 'password_image'
        input = Input(type = 'password',
                      id = 'password_input',
                      title = 'PASSWORD',
                      placeholder = 'Enter password',
                      onchange = 'checkLogin()')

    return {'image': image,
            'image_id': image_id,
            'i': input,
            'last': last}


class Button:
    def __init__(self, image=None, text=None, delete=False, onclick=None, index=None, disabled=False):
        self.image = image
        self.text = text
        self.delete = delete
        self.onclick = onclick
        self.index = index
        self.disabled = disabled

@register.inclusion_tag('button.html')
def button(type, a=None, b=None, context=None, id=None):
    buttons = []
    
    if type == 'one':
        if a == 'product_popup':
            text = 'BUY'
            onclick = "productPopup(id='{}', model='{}')".format(context.id, context.model)
            index = 'product_{}'.format(id)
            disabled = False

        elif a == 'login':
            text = 'CONTINUE'
            onclick = 'login()'
            index = 'login'
            disabled = True

        elif a == 'register':
            text = 'COMPLETE'
            onclick = 'register()'
            index = 'register'
            disabled = True

        elif a == 'account_save':
            text = 'SAVE'
            onclick = 'accountSave()'
            index = 'account'
            disabled = False

        buttons.append(Button(
            text = text,
            onclick = onclick,
            index = index,
            disabled = disabled
        ))
        
    elif type == 'two':
        lst = [a, b]
        for x in lst:
            if x == 'item_popup':
                image = '/static/images/edit.png'
                delete = False
                onclick = "itemPopup(id='{}', model='{}')".format(context.id, context.product.model)

            elif x == 'cart_delete':
                image = '/static/images/delete.png'
                delete = True
                onclick = "cartDelete(id='{}', model='{}')".format(context.id, context.product.model)

            elif x == 'cart_delete_all':
                image = '/static/images/delete.png'
                delete = True
                onclick = 'cartDeleteAll()'

            elif x == 'cart_submit':
                image = '/static/images/done.png'
                delete = False
                onclick = 'cartSubmit()'
            
            buttons.append(Button(
                image = image,
                delete = delete,
                onclick = onclick
            ))

    return {'type': type,
            'buttons': buttons}