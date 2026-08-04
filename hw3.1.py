a = float(input("enter first number --> "))
b = float(input("enter second number --> "))
op = input("choose operation -->(+, -,  *, / ): ")

if op == "+":
    print("result-->", a + b)
elif op == "-":
    print("result-->", a - b)
elif op == "*":
    print("result-->", a * b)
elif op == "/":
    if b == 0:
        print("error")
    else:
        print("result-->", a / b)
else:
    print("error")
