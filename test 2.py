def arr_of_str_to_2darr(list: list, reverse: bool): # reverse function for if you want 2darr to str instead of str to 2darr 
    out = []
    if reverse:
        for line in list:
            out.append("".join(line))
    else:
        for i in range(len(list)): 
            out.append([])
            for chr in list[i]:
                out[i].append(chr)

    return out


arr = [['a','a','a','a','a','a','a'],['a','a','a','a','a','a','a'],['a','a','a','a','a','a','a']]

print(arr_of_str_to_2darr(arr, True))