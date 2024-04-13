from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from app.views import *


urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # login
    path('login/', login_view, name='login_view'),
    path('login_account/', login_account, name='login_account'),

    # logout
    path('logout_account/', logout_account, name='logout_account'),

    # register
    path('register/', register_view, name='register_view'),
    path('register_account/', register_account, name='register_account'),

    # home
    path('', home_view, name='home_view'),

    # account
    path('account/', account_view, name='account_view'),
    path('account_save/', account_save, name='account_save'),

    # products
    path('products/', products_view, name='products_view'),
    path('product_popup/', product_popup, name='product_popup'),
    path('item_popup/', item_popup, name='item_popup'),

    # cart
    path('cart/', cart_view, name='cart_view'),
    path('cart_add/', cart_add, name='cart_add'),
    path('cart_save/', cart_save, name='cart_save'),
    path('cart_delete/', cart_delete, name='cart_delete'),
    path('cart_delete_all/', cart_delete_all, name='cart_delete_all'),
    path('cart_submit/', cart_submit, name='cart_submit'),

    # orders/order
    path('orders/', orders_view, name='orders_view'),
    path('order/<id>/', order_view, name='order_view'),
    path('order_save/', order_save, name='order_save'),
    path('order_popup/', order_popup, name='order_popup'),

    # users/user
    path('users/', users_view, name='users_view'),
    path('user/<id>/', user_view, name='user_view'),

    # user analysis
    path('user_analysis/<id>/', user_analysis_view, name='user_analysis_view'),
    
    # financy
    path('financy/', financy_view, name='financy_view')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)