

def check_is_right(array, string, count):
    return array[count-1][1] if string.find('f\'c') == -1 or string.find('fc') == -1 else 'True'

def get_the_num(string):
    indices = [j for j, k in enumerate(string) if k in [' ', '=']]
    if len(indices) < 2:
        indices.append(indices[0])
        for c, char in enumerate(string):
            if char == '2':
                indices[0] = c
                break
    return string[indices[0]+1 : indices[1]]