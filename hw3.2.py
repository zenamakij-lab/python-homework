def move_last_to_first(lst):
    if len(lst) <= 1:
        return lst
    return [lst[-1]] + lst[:-1]


print(move_last_to_first([12, 3, 4, 10]))
print(move_last_to_first([1]))
print(move_last_to_first([]))
print(move_last_to_first([12, 3, 4, 10, 8]))
