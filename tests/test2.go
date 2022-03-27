package main

import "fmt";

func zeroval(ival int) {
    ival = 0;
}

func zeroptr(iptr *int) {
    *iptr = 0;
}

func main() {
    i := 1;
    var x float = 1.0;
    y := 2.0;
    if true || false {
        zeroval(i);
        zeroptr(&i);
    }
    
    j := (x + 1.0) == x;
    k := &j;
    i = +3;
    i = 4;
}