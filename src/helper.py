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
