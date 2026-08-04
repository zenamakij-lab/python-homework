
import string
import keyword

name = input()

def is_valid_variable(name: str) -> bool:

    if name in keyword.kwlist:
        return False


    if name[0].isdigit():
        return False


    if name.count("_") > 1:
        return False


    forbidden = set(string.punctuation.replace("_", "") + " ")
    if any(char in forbidden for char in name):
        return False

    # не повинно бути великих літер
    if any(char.isupper() for char in name):
        return False

    return True


print(is_valid_variable(name))
