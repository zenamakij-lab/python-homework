
def string_length(text):
    return len(text)


def join_strings(text1, text2):
    return text1 + text2





def square(number):
    return number ** 2


def add_numbers(a, b):
    return a + b


def divide_numbers(a, b):
    whole = a // b
    remainder = a % b
    return whole, remainder




def average(numbers):
    return sum(numbers) / len(numbers)


def common_elements(list1, list2):
    return list(set(list1) & set(list2))




def print_keys(dictionary):
    for key in dictionary.keys():
        print(key)


def merge_dictionaries(dict1, dict2):
    return dict1 | dict2
    




def union_sets(set1, set2):
    return set1 | set2

def is_subset(set1, set2):
    return set1.issubset(set2)





def even_or_odd(number):
    if number % 2 == 0:
        return "Парне"
    else:
        return "Непарне"


def even_numbers(numbers):
    result = []
    for number in numbers:
        if number % 2 == 0:
            result.append(number)
    return result



check_even = lambda x: "Парне" if x % 2 == 0 else "Не парне"




print(string_length("Привіт"))
print(join_strings("Привіт, ", "світ!"))

print(square(5))
print(add_numbers(7, 8))
print(divide_numbers(17, 5))

print(average([2, 4, 6, 8]))
print(common_elements([1, 2, 3, 4], [3, 4, 5, 6]))

print_keys({"ім'я": "женя", "вік": 17})

print(merge_dictionaries({"a": 1}, {"b": 2}))

print(union_sets({1, 2}, {2, 3, 4}))
print(is_subset({1, 2}, {1, 2, 3}))

print(even_or_odd(10))
print(even_numbers([1, 2, 3, 4, 5, 6]))

print(check_even(7))
print(check_even(8))