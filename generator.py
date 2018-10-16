def sorting(positions):
    iterators = []
    for lst in positions:
        iterators.append(iter(lst))

    min_list = [next(lst) for lst in iterators]    
    while min_list != []:
        #print(min_list)
        min_el = min(min_list)
        i = min_list.index(min_el)
        try:
            min_list[i] = next(iterators[i])
        except StopIteration:
            min_list.remove(min_el)
            iterators.pop(i)
        yield(min_el)
        
array = [[1, 4 , 5], [4, 5, 12, 39, 78], [0, 4, 55, 66], [0]]
#positions = list(sorting(array))
#print(positions)
