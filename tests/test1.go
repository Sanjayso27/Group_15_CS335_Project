package main


func fun(a struct{x,y int;}) bool{
	if a.x*a.x > a.y{
		return true;
	} else {
		return false;
	}
}

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

func main(){
	var b struct{x,y int;};
	b.x = 4;
	b.y = 6;
	var ans int;
	ans = 4 * -2 + 3 * -1;
}