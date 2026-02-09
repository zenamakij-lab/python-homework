import string

s = input()
a, b = s.split("-")

letters = string.ascii_letters
print(letters[letters.index(a):letters.index(b) + 1])
