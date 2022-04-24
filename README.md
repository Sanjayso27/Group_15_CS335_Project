# Compiler-Design-Group-15
Designing Compiler of Go in Python

# How to run

Install PLY package by using
```pip install ply```

Give executing permission
```chmod u+x go.sh```

To run lexer on test case in work_tests/ use
```./gosh name_of_the_file(without .go extension)``` for eg ``` ./gosh if_else```

### references
- [Test cases](https://gobyexample.com/)
- [PLY documentation](https://ply.readthedocs.io/en/latest/ply.html)
- [Go documentation](https://go.dev/ref/spec)
- [ANSI grammar](https://www.lysator.liu.se/c/ANSI-C-grammar-y.html)
- [GoLang](https://go.dev/ref/spec)
- [Pike](https://github.com/raghukul01/Pike)
- Our Symbol table structure and type dictionary structure is referenced from the above repo.We have understood the semantic analysis from this repo and modified it according to our grammar rules. We also understood and modified the implementation of multi-D arrays and offset calculation,returning structs,pointers,structs and pointer as params,floating point instructions,assigning structs,I/O  from this repo for our purpose.

