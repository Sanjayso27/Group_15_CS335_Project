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
    //Println("initial:", i);

    zeroval(i);
    //Println("zeroval:", i);

    zeroptr(&i);
    //Println("zeroptr:", i);

    //Println("pointer:", &i);
}