from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import app.models_local as local
from .utils import *


MESSAGE_CHOICES = [
    ('order_sent', 'Order sent'),
    ('order_recieved', 'Order recieved'),
    ('order_status_updated', 'Order status updated'),
]

MATERIAL_CHOICES = [
    ('standard', 'Standard [-40\xb0C to +60\xb0C]'),
    ('high_temp_1', 'High Temp 1 [-40\xb0C to +100\xb0C]'),
    ('high_temp_2', 'High Temp 2 [-40\xb0C to +120\xb0C]'),
    ('high_temp_3', 'High Temp 3 [-40\xb0C to +140\xb0C]')
]

COLOR_CHOICES = [
    ('black', 'Black'),
    ('white', 'White'),
    ('custom', 'Custom')
]

ORDER_STATUS_CHOICES = [
    ('-', '-'),
    ('recieved', 'Recieved'),
    ('in_process', 'In process'),
    ('shipped', 'Shipped')
]

ORDER_SORT_CHOICES = [
    ('price_up', 'Price Up'),
    ('price_down', 'Price Down'),
    ('date_up', 'Date Up'),
    ('date_down', 'Date Down')
]
ORDER_SORT_DEFAULT = ORDER_SORT_CHOICES[3][0]

USER_SORT_CHOICES = [
    ('orders_up', 'Orders Up'),
    ('orders_down', 'Orders Down'),
    ('price_up', 'Price Up'),
    ('price_down', 'Price Down')
]
USER_SORT_DEFAULT = USER_SORT_CHOICES[3][0]


class UserManager(BaseUserManager):
	def create_user(self, email, password):
		if not email:
			raise ValueError('User must have an email address')
		if not password:
			raise ValueError('User must have a password')

		user = self.model(
			email = self.normalize_email(email)
		)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, password):
		user = self.create_user(
			email = self.normalize_email(email),
			password = password
		)
		user.is_active = True
		user.is_admin = True
		user.save()
		return user


class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=200, unique=True, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    date_joined	= models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    class Meta:
        db_table = 'users'

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    # id | full name
    def __str__(self):
        return '{} | {}'.format(self.id, self.full_name)

    # first name last name (company)
    @property
    def full_name(self):
        return '{} {} ({})'.format(self.first_name, self.last_name, self.company) if self.company else '{} {}'.format(self.first_name, self.last_name)

    @property
    def location(self):
        return '{}, {}'.format(self.address, self.country)

    def orders(self, year):
        if year == 'all':
            return Order.objects.filter(user=self).order_by('-ordered_date')
        else:
            return Order.objects.filter(user=self, ordered_date__year=year).order_by('-ordered_date')

    def count_orders(self, year):
        return self.orders(year).count()

    def orders_total_price(self, year):
        return sum([order.price for order in self.orders(year)])

    def orders_by_months(self, year):
        # create list of months in format [MONTH, ORDERS COUNT]
        lst = prepare_orders_by_months()
        
        for order in self.orders(year):
            # increase order count for the month that the order has been made in
            lst[order.ordered_date.month-1][1] += 1
        
        # new list without months with 0 orders
        lst2 = [x for x in lst if x[1] > 0]
        return lst2
    
    def items(self, year):
        items_list = []
        for order in self.orders(year):
            for item in order.items.all():
                added = False

                # check if already exists item with the same name
                for i in items_list:
                    if i.name == item.product.name:
                        # exists: add material, color, amount, price
                        i.add_values(
                            material = item.material.name,
                            color = item.color.name,
                            amount = item.amount,
                            price = item.price
                        )
                        # exit loop
                        added = True
                        break

                # if doesn't exist - add new item to list
                if not added:
                    new_item = local.ItemLocal(
                        name = item.product.name,
                        material = item.material.name,
                        color = item.color.name,
                        amount = item.amount,
                        price = item.price
                    )
                    items_list.append(new_item)

        # sort and convert materials & colors
        for item in items_list:
            item.sort()
            item.convert()

        # sort items by price
        items_list = sorted(items_list, key=lambda i:i.price, reverse=True)
        return items_list


class Material(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, choices=MATERIAL_CHOICES, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'materials'

    # name (price €)
    def __str__(self):
        return '{} ({} \u20ac)'.format(self.name, self.price)


class Color(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, choices=COLOR_CHOICES, blank=True, null=True)

    class Meta:
        db_table = 'colors'

    # name
    def __str__(self):
        return '{}'.format(self.name)


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.FileField(upload_to='models/', blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    public = models.BooleanField(default=False)
    exclusive_for = models.ManyToManyField(User, related_name='exclusive_products', blank=True)
    amount_min = models.IntegerField(blank=True, null=True)
    materials = models.ManyToManyField(Material, blank=True)
    colors = models.ManyToManyField(Color, blank=True)

    class Meta:
        db_table = 'products'

    # id | name
    def __str__(self):
        return '{} | {}'.format(self.id, self.name)

    @property
    def model_url(self):
        return self.model.url if self.model else ''

                
class Item(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True)
    custom_color = models.CharField(max_length=20, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'items'

    # id | product name (material, color, amount)
    def __str__(self):
        return '{} | {} ({}, {}, {})'.format(self.id, self.product.name, self.material, self.color, self.amount)

    def save(self, *args, **kwargs):
        self.price = self.total_price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.amount * self.material.price

        
class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    items = models.ManyToManyField(Item, blank=True)
    
    class Meta:
        db_table = 'carts'

    # CART #id | full name | items count | amount | € price
    def __str__(self):
        return 'CART #{} | {} | {} items | {} amount | {} \u20ac price'.format(self.id, self.user.full_name, self.count_items, self.total_amount, self.total_price)

    # checks if there is an existing item with the same specifications but different id
    # if there is - add amount from new item to the same item in items list
    def has_same_item(self, item):
        query = False
        for i in self.items.all():
            if i.id != item.id:
                # check if product, material and color are the same
                if i.product == item.product and i.material == item.material and i.color == item.color:
                    # if color is custom and custom color is the same or color is not custom
                    if (i.color.name == 'custom' and i.custom_color == item.custom_color) or i.color.name != 'custom':
                        # add amount to existing item
                        i.amount += item.amount
                        i.save()

                        query = True
                        break
        return query

    @property
    def count_items(self):
        return self.items.count()

    @property
    def total_amount(self):
        return sum([item.amount for item in self.items.all()])

    @property
    def total_price(self):
        return sum([item.price for item in self.items.all()])
    
        
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='orders_set', on_delete=models.CASCADE, blank=True, null=True)
    items = models.ManyToManyField(Item, blank=True)
    ordered_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_CHOICES[0][0])
    in_process_date = models.DateField(blank=True, null=True)
    shipped_date = models.DateField(blank=True, null=True)
    items_count = models.IntegerField(blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    
    class Meta:
        db_table = 'orders'

    # ORDER #id (ordered date) | full name | items count | amount | € price
    def __str__(self):
        return 'ORDER #{0} ({1.day}.{1.month}.{1.year}. {1.hour:02d}:{1.minute:02d}) | {2} | {3} items | {4} amount | {5} \u20ac price'.format(self.id, self.ordered_date, self.user.full_name, self.items_count, self.amount, self.price)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # on call .save(update_fields=...) - only selected fields are updated, inner part is skipped
        if update_fields is None:
            # on obj creation - id is null and the following is skipped
            # on call .save() - the following is executed (should be called only once, after obj creation)
            if self.id and self.items:
                self.items_count = self.count_items
                self.amount = self.total_amount
                self.price = self.total_price
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    @property
    def count_items(self):
        return self.items.count()

    @property
    def total_amount(self):
        return sum([item.amount for item in self.items.all()])

    @property
    def total_price(self):
        return sum([item.price for item in self.items.all()])

        
class Message(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=30, choices=MESSAGE_CHOICES, blank=True, null=True)
    for_admin = models.BooleanField(default=False)
    for_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, blank=True, null=True)
    order_status_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'messages'

    # MESSAGE #id (date) | ORDER #id | type: | status:
    def __str__(self):
        return 'MESSAGE #{0} ({1.day}.{1.month}.{1.year}. {1.hour:02d}:{1.minute:02d}) | ORDER #{2} | {3} | {4}'.format(self.id, self.date, self.order.id, self.get_type_display(), self.get_order_status_display())

    # on call .save() - set content and order status fields
    def save(self, *args, **kwargs):
        self.order_status = self.order.order_status
        
        if self.type == MESSAGE_CHOICES[0][0]:
            self.content = 'ORDER #{} successfully sent'.format(self.order.id)
        elif self.type == MESSAGE_CHOICES[1][0]:
            self.content = 'Recieved new order - ORDER #{}'.format(self.order.id)
        elif self.type == MESSAGE_CHOICES[2][0]:
            self.content = 'Updated status for ORDER #{}'.format(self.order.id)        
            
            if self.order_status == ORDER_STATUS_CHOICES[2][0]:
                self.order_status_date = self.order.in_process_date
            elif self.order_status == ORDER_STATUS_CHOICES[3][0]:
                self.order_status_date = self.order.shipped_date     
                
        super().save(*args, **kwargs)

    @property
    def order_status_display(self):
        if self.order_status == ORDER_STATUS_CHOICES[2][0]:
            return 'IN PROCESS DATE'
        elif self.order_status == ORDER_STATUS_CHOICES[3][0]:
            return 'SHIPPED DATE'
        else:
            return ''

    @property
    def order_status_image(self):
        if self.order_status == ORDER_STATUS_CHOICES[2][0]:
            return '/static/images/in_process.png'
        elif self.order_status == ORDER_STATUS_CHOICES[3][0]:
            return '/static/images/shipped.png'
        else:
            return ''