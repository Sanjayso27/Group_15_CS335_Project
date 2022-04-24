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
    if (n == 0) {
        return 0;
    };
	if (n==1){
		return 1;
	};
    return fib(n-1) + fib(n-2);
};

func fac(n int) int {
    if n<=1 {
        return 1;
    };
    return n*fac(n-1);
};
func chk(n int) int {
	return n+1;
};

// Mutual recursion
func odd (n int) int;
func even (n int) int;

func odd(n int)int {
	if n==1 {
		return 1;
	};
	if n==0 {
		return 0;
	};
	return even(n-1);
};

func even(n int)int {
	if n==1 {
		return 0;
	};
	if n==0 {
		return 1;
	};
	return odd(n-1);
};

// Function Overloading
func sum(a int,b int) int{
	return a+b;
};

func sum(a int,b int,c int)int {
	return a+b+c;
};

func sum(a [1]int,b [1]int)int{
	return a[0]+b[0];
};

func main(){
    print A(3,4);	// 125
	print A(0,0);	// 1
    print fib(3);	// 2
    print fac(2);	// 2
	print chk(2);	// 3
	print even(4);	// 1
	print odd(2);	// 0
	print sum(1,2); // 3
	print sum(1,2,3); // 6
	var a[1] int;
	var b[1] int;
	a[0]=1; b[0]=2;
	print sum(a,b); // 3
};