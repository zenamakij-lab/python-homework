def move_zeros(lst):
    non_zeros = []
    zeros_count = 0

    for x in lst:
        if x == 0:
            zeros_count += 1
        else:
            non_zeros.append(x)

    return non_zeros + [0] * zeros_count


print(move_zeros([0, 1, 0, 12, 3]))
print(move_zeros([0]))
print(move_zeros([1, 0, 13, 0, 0, 0, 5]))
print(move_zeros([9, 0, 7, 31, 0, 45, 0, 45, 0, 45, 0, 0, 96, 0]))
