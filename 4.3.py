import random


length = random.randint(3, 10)
lst = [random.randint(1, 10) for _ in range(length)]


new_lst = [lst[0], lst[2], lst[-2]]


print(lst, "==", new_lst)
