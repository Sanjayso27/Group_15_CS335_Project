from numpy import isin
from rich.console import Console
from rich.table import Table

console = Console()

def print_error(msg, lineno, colno):
    console.print("ERROR", style = "bold underline red", end = "")
    console.print(f" L:{lineno} C:{colno}", style="bold", end = "")
    console.print(" : ", msg)

def print_warn(msg, lineno, colno):
    console.print("WARNING", style = "bold underline violet", end = "")
    console.print(f" L:{lineno} C:{colno}", style="bold", end = "")
    console.print(" : ", msg)
    

def print_table(headers, data):
    table = Table()
    for col in headers:
        table.add_column(str(col))
    for row in data:
        r = [str(x) for x in row]
        table.add_row(*r)
    console.print(table)

def print_csv(headers, data, filename):
    f = open(filename, mode='w')
    for h in headers :
        f.write(f"{h}, ")
    f.write("\n")
    for row in data :
        for h in row :
            f.write(f"{h}, ")
        f.write("\n")
    f.close()


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



