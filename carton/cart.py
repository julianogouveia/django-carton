from decimal import Decimal

from carton import settings as carton_settings


class CartItem:
    def __init__(self, variant_id, image, name, quantity, price, data={}):
        self.variant_id = variant_id
        self.image = image
        self.name = name
        self.quantity = int(quantity)
        self.price = Decimal(str(price))
        self.data = data

    def __repr__(self):
        return 'Product variant ({})'.format(self.variant_id)

    def to_dict(self):
        return {
            'variant_id': self.variant_id,
            'image': self.image,
            'name': self.name,
            'quantity': self.quantity,
            'price': str(self.price),
            'data': self.data,
        }

    @property
    def subtotal(self):
        return self.price * self.quantity


class Cart:
    def __init__(self, session, session_key=None):
        self._items_dict = {}
        self.session = session
        self.session_key = session_key or carton_settings.CART_SESSION_KEY

        if self.session_key in self.session:
            cart_representation = self.session[self.session_key]
            ids_in_cart = cart_representation.keys()

            for variant_id in ids_in_cart:
                item = cart_representation[variant_id]

                self._items_dict[variant_id] = CartItem(
                    item['variant_id'], item['image'], item['name'], 
                    item['quantity'], Decimal(item['price']), data=item['data']
                )

    def __contains__(self, variant_id):
        return variant_id in self._items_dict

    def update_session(self):
        self.session[self.session_key] = self.cart_serializable
        self.session.modified = True

    def add(self, variant_id, image, name, price=None, quantity=1, data={}):
        quantity = int(quantity)

        if quantity < 1:
            raise ValueError('Quantity must be at least 1 when adding to cart')

        if variant_id in self._items_dict:
            self._items_dict[variant_id].quantity += quantity
        else:
            if price == None:
                raise ValueError('Missing price when adding to cart')
            self._items_dict[variant_id] = CartItem(variant_id, image, name, quantity, price, data=data)

        self.update_session()

    def remove(self, variant_id):
        del self._items_dict[variant_id]
        self.update_session()

    def remove_single(self, variant_id):
        if variant_id in self._items_dict:
            if self._items_dict[product.pk].quantity <= 1:
                # There's only 1 product left so we drop it
                del self._items_dict[product.pk]
            else:
                self._items_dict[product.pk].quantity -= 1
            self.update_session()

    def clear(self):
        self._items_dict = {}
        self.update_session()

    def set_quantity(self, variant_id, quantity):
        quantity = int(quantity)

        if quantity < 0:
            raise ValueError('Quantity must be positive when updating cart')

        if variant_id in self._items_dict:
            self._items_dict[variant_id].quantity = quantity

            if self._items_dict[variant_id].quantity < 1:
                del self._items_dict[variant_id]

            self.update_session()

    @property
    def items(self):
        return self._items_dict.values()

    @property
    def cart_serializable(self):
        cart_representation = {}

        for item in self.items:
            product_id = str(item.variant_id)
            cart_representation[product_id] = item.to_dict()

        return cart_representation

    @property
    def items_serializable(self):
        return self.cart_serializable.items()

    @property
    def count(self):
        return sum([item.quantity for item in self.items])

    @property
    def unique_count(self):
        return len(self._items_dict)

    @property
    def is_empty(self):
        return self.unique_count == 0

    @property
    def products(self):
        return [item.variant_id for item in self.items]

    @property
    def total(self):
        return sum([item.subtotal for item in self.items])