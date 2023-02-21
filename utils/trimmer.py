import copy

def trim(lines):

    keyValueList = copy.deepcopy(lines)  
    # Create a pop list of indices to remove because missing key=value pairs.
    popList = []
    
    for i,v in enumerate(keyValueList):
        if '=' not in v:
            popList.append(i)
    
    # Remove indices in popList
    for index in sorted(popList, reverse=True):
        del keyValueList[index]

    # Create dictionary from trimmed list
    keyValues_dict = dict(s.split('=',1) for s in keyValueList)
    
    return keyValues_dict, popList