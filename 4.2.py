def even_index_sum_mult_last(lst):
    if not lst:
        return 0

    even_index_sum = 0
    for i in range(0, len(lst), 2):
        even_index_sum += lst[i]

    return even_index_sum * lst[-1]



print(even_index_sum_mult_last([0, 1, 7, 2, 4, 8]))
print(even_index_sum_mult_last([1, 3, 5]))
print(even_index_sum_mult_last([6]))
print(even_index_sum_mult_last([]))