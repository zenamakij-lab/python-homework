class Product:
    def __init__(self, name, category, price, quantity):
        self.name = name
        self.category = category
        self.price = float(price)
        self.quantity = int(quantity)

    def change_price(self, new_price):
        self.price = new_price

    def change_quantity(self, new_quantity):
        self.quantity = new_quantity

    def __str__(self):
        return f"{self.name} | {self.category} | {self.price} грн | {self.quantity} шт."


class Order:
    def __init__(self):
        self.products = []
        self.total = 0

    def add_product(self, product, quantity):
        if product.quantity >= quantity:
            self.products.append((product, quantity))
            product.quantity -= quantity
            self.calculate_total()
        else:
            print(f"Недостатньо товару: {product.name}")

    def calculate_total(self):
        self.total = 0
        for product, quantity in self.products:
            self.total += product.price * quantity

    def __str__(self):
        text = "Замовлення:\n"
        for product, quantity in self.products:
            text += f"- {product.name} x {quantity}\n"
        text += f"Загальна сума: {self.total} грн"
        return text


class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)

    def __str__(self):
        return f"{self.name} ({self.email})"


def load_products(filename):
    products = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            name, category, price, quantity = line.strip().split(";")
            products.append(Product(name, category, price, quantity))

    return products



products = load_products("products.txt")



print("Товари магазину:")
for product in products:
    print(product)


customer = Customer("zhenya", "zenamakij@gmail.com")


order = Order()


order.add_product(products[0], 2)
order.add_product(products[1], 1)


customer.add_order(order)

print("\nКлієнт:")
print(customer)

print("\nІнформація про замовлення:")
print(order)

print("\nЗалишок товарів на складі:")
for product in products:
    print(product)