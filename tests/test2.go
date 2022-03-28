package main

import "fmt";

func zeroval(ival int) {
    ival = 0;
}

func zeroptr(iptr *int) {
    *iptr = 0;
}

func fib(n int) int {
    if n == 0 || n == 1 {
        return 0;
    }
    return fib(n-1) + fib(n-2);
}

func main() {
    i := 1;
    var x float = 1.0;
    y := 2.0;
    if true || false {
        zeroval(*&i);
        zeroptr(&i);
    }

    var arr [3]int;
    arr[0] = 1;

    x = 1.0;
    var z struct{x int; y struct{x, y int;};};
    z.y.x = 1;
    
    j := (x + 1.0) == x;
    k := &j;
    i = +3;
    i = 4;
}