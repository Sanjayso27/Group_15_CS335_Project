package main

import "fmt";

func zeroval(ival int) {
    ival = 0;
}

func zeroptr(iptr *int) {
    *iptr = 0;
}

func main() {
    if i := 1; i==1 {
        zeroval(i);
        zeroptr(&i);
    } else if i==1 {
        zeroval(i);
        zeroptr(&i);
    } else {
        zeroval(i);
        zeroptr(&i);
    }

}