print ("task number one")

number = float(input("enter number--> "))
print("square of number isss --->", number ** 2)

print ("task number dva")

a = float(input("first number-->: "))
b = float(input("second number--> "))
c = float(input("third number-->"))

average = (a + b + c) / 3
print("average-->", average)

print ("task number three")

minutes = int(input("how much minutes-->: "))
hours = int(input("how much hours-->: "))

hours = minutes // 60
remaining_minutes = minutes % 60

print(hours, "hours", remaining_minutes, "minutes")

print("task number four")

price = float(input("enter price-->: "))
discount = float(input("enter discount-->: "))

final_price = price - price * discount / 100
print("price with sale -->", final_price)

print("task number five")

number = int(input("enter number-->: "))
last_digit = (number) % 10

print("last number-->", last_digit)

print("task number six")

length = float(input("enter length-->: "))
width = float(input("enter width-->: "))

perimeter = 2 * (length + width)
print("perimeter-->", perimeter)

print("task number seven")

number = int(input("enter 4 numbers -->: "))

digit1 = number // 1000
digit2 = (number // 100) % 10
digit3 = (number // 10) % 10
digit4 = number % 10

print(digit1)
print(digit2)
print(digit3)
print(digit4)


print("finish!!!")
