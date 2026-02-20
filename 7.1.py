def say_hi(name, age):
    return "Hi. My name is Женя and I\'m {0} years old".format(str(16))


assert say_hi("Alex", 32) == "Hi. My name is Женя and I'm 32 years old", 'Test1'
assert say_hi("Frank", 68) == "Hi. My name is Женя and I'm 68 years old", 'Test2'
print('ОК')
