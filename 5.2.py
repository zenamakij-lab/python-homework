while True:
    a = float(input("enter first number--> "))
    op = input("choose operation--> (+, -, *, /): ")
    b = float(input("choose second number--> "))

    if op == "+":
        result = a + b
    elif op == "-":
        result = a - b
    elif op == "*":
        result = a * b
    elif op == "/":
        if b == 0:
            print("fail")
            continue
        result = a / b
    else:
        print("fail")
        continue

    print("result-->", result)

    cont = input("continue?? (yes): ").lower()
    if cont not in ( "yes"):
        break

print("break")
