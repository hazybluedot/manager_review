def num_or_string(value):
    try:
        return float(value)
    except ValueError:
        return value

def flatten_list(l):        
    return [ item for sublist in l for item in sublist ] # flatten list of lists

def issumable(thing):
    try:
        1.0 + thing
    except TypeError:
        return False
    else:
        return True
