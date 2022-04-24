package main;

func A(m int, n int) int {
    if m == 0 {
        return n+1;
    };
    if (m > 0) && (n == 0) {
        return A(m-1, 1);
    };
    return A(m-1, A(m, n-1));
};

func fib(n int) int {
    if (n == 0) || (n == 1) {
        return 0;
    };
    return fib(n-1) + fib(n-2);
};

func fac(n int) int {
    if n<=1 {
        return 1;
    };
    return n*fac(n-1);
};

func main(){
    if (1<2) && (2<3){
        print "Hello";
    };
    A(3,4);
    fib(3);
    fac(2);
};