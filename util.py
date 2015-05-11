def num_or_string(value):
    try:
        return float(value)
    except ValueError:
        return value

def num_or_none(fn, value):
    try:
        return fn(value)
    except ValueError:
        return None
    
def flatten_list(l):        
    return [ item for sublist in l for item in sublist ] # flatten list of lists

def issumable(thing):
    try:
        1.0 + thing
    except TypeError:
        return False
    else:
        return True

def label_to_attr(string):
    return string.lower().replace(' ','_')

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
