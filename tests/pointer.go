package main;

func zeroptr(iptr *int) {
    *iptr = 0;
};

func main() {
	var x,y int;
	var ptr *int;
	zeroptr(ptr);
	x =*ptr;

	print x;
};