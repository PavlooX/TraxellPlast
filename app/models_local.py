from abc import abstractmethod
import app.models as m
from .utils import *


class Info:
    def __init__(self, name, amount):
        self.name = name
        self.display = self.name_display
        self.amount = amount

    @property
    @abstractmethod
    def name_display(self):
        pass


class MaterialLocal(Info):
    @property
    def name_display(self):
        for material in m.MATERIAL_CHOICES:
            if material[0] == self.name:
                return material[1]
        return None
    

class ColorLocal(Info):
    @property
    def name_display(self):
        for color in m.COLOR_CHOICES:
            if color[0] == self.name:
                return color[1]
        return None


class ItemInfo:
    def __init__(self):
        self.materials = []
        self.materials_list = []
        self.colors = []
        self.colors_list = []
        self.amount = 0
        self.price = 0

    # if material exists - add amount to that material
    def material_exists(self, material, amount):
        exists = False
        for mat in self.materials:
            if mat.name == material:
                mat.amount += amount
                exists = True
                break
        return exists

    # if material doesn't exist - add new material
    def material_add(self, material, amount):
        new_mat = MaterialLocal(
            name = material,
            amount = amount
        )
        self.materials.append(new_mat)

    def color_exists(self, color, amount):
        exists = False
        for col in self.colors:
            if col.name == color:
                col.amount += amount
                exists = True
                break
        return exists

    def color_add(self, color, amount):
        new_color = ColorLocal(
            name = color,
            amount = amount
        )
        self.colors.append(new_color)

    # sort materials & colors by amount
    def sort(self):
        self.materials = sorted(self.materials, key=lambda m:m.amount, reverse=True)
        self.colors = sorted(self.colors, key=lambda c:c.amount, reverse=True)

    # convert materials & colors from objects to readable list
    def convert(self):
        for mat in self.materials:
            self.materials_list.append((mat.display.upper(), mat.amount))
        for col in self.colors:
            self.colors_list.append((col.display.upper(), col.amount))


class ItemLocal(ItemInfo):
    def __init__(self, name, material, color, amount, price):
        self.name = name
        super().__init__()
        self.add_values(material=material, color=color, amount=amount, price=price)

    def add_values(self, material, color, amount, price):
        # material
        if not self.material_exists(material, amount):
            self.material_add(material, amount)

        # color
        if not self.color_exists(color, amount):
            self.color_add(color, amount)
        
        self.amount += amount
        self.price += price
   

class ItemsAnalysisLocal(ItemInfo):
    def __init__(self, items):
        self.items = items
        super().__init__()

    @property
    def values(self):
        # analyze items
        for item in self.items:
            self.check_values(item.materials, item.colors, item.amount, item.price)

        # sort and convert materials & colors
        self.sort()
        self.convert()

        # results
        return {'materials': self.materials_list,
                'colors': self.colors_list,
                'amount': self.amount,
                'price': self.price}

    def check_values(self, materials, colors, amount, price):
        # materials
        for mat in materials:
            if not self.material_exists(mat.name, mat.amount):
                self.material_add(mat.name, mat.amount)

        # colors
        for col in colors:
            if not self.color_exists(col.name, col.amount):
                self.color_add(col.name, col.amount)
        
        self.amount += amount
        self.price += price


class FinancyLocal:
    def __init__(self, year):
        self.orders_analysis(year)
        self.products_analysis()
        self.expensive_analysis(year)
        self.cheap_analysis(year)

    def orders_analysis(self, year):
        # orders & users
        if year == 'all':
            self.orders = m.Order.objects.all()
            self.users = sorted(m.User.objects.filter(orders_set__gt=0).distinct(), key=lambda u:u.orders_total_price(year), reverse=True)
        else:
            self.orders = m.Order.objects.filter(ordered_date__year=year)
            self.users = sorted(m.User.objects.filter(orders_set__ordered_date__year=year).distinct(), key=lambda u:u.orders_total_price(year), reverse=True)

        # orders count
        self.orders_count = len(self.orders)

        # orders total price & orders months
        self.orders_total_price = 0
        lst = prepare_orders_by_months()
        for order in self.orders:
            lst[order.ordered_date.month-1][1] += 1
            self.orders_total_price += order.price
        self.orders_months = [x for x in lst if x[1] > 0]

    @property
    def retrieve_items(self):
        items_list = []
        for order in self.orders:
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
                    new_item = ItemLocal(
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

    def products_analysis(self):
        # items
        self.items = self.retrieve_items

        # items count
        self.items_count = len(self.items)

        # items materials, colors, amount and price
        items_analysis = ItemsAnalysisLocal(self.items)
        values = items_analysis.values
        self.items_materials = values['materials']
        self.items_colors = values['colors']
        self.items_amount = values['amount']
        self.items_price = values['price']

    def expensive_analysis(self, year):
        if year == 'all':
            self.expensive = m.Order.objects.all().order_by('-price').first()
        else:
            self.expensive = m.Order.objects.filter(ordered_date__year=year).order_by('-price').first()

    def cheap_analysis(self, year):
        if year == 'all':
            self.cheap = m.Order.objects.all().order_by('price').first()
        else:
            self.cheap = m.Order.objects.filter(ordered_date__year=year).order_by('price').first()