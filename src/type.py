def typestring(typelist):
    if isinstance(typelist, str) :
        return typelist
    if isinstance(typelist, list) :
        if typelist[0] == 'PTR':
            return '*'+typestring(typelist[1])
        elif typelist[0] == 'SLICE' :
            return '[]' + typestring(typelist[1])
        elif typelist[0] == 'ARR' :
            return '[]' + typestring(typelist[2])
        else :
            s = 'struct{'
            for id in typelist[1].keys() :
                s += f"{id} {typestring(typelist[1][id])}; "
            s += '}'
            return s