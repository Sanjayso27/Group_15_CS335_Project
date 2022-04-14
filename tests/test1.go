package main;
import "fmt";

func fun(a struct{x,y int;}) bool {
	if a.x*a.x > a.y {
		return true
	} else {
		return false
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
	b.x = 4
	b.y = 6
	x := &b
	if b.x == 5 {
		b.x = 4
	} else {
		b.x = 3
	}
	var ans int;
	ans = 4 * -b.x + 3 * -b.y;
	ans = 1;
	fmt.Println(ans)
};