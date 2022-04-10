package main

import "fmt";

func fact(n int) int {
    if n == 0 {
        return 1;
    }
    return n * fact(n-1);
}


func fib(n int) int {
    if n == 0 || n == 1 {
        return 0;
    }
    return fib(n-1) + fib(n-2);
}

func main() {
    fmt.Println(fact(7));
}