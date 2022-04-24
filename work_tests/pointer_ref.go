package main;

func main(){
	var y ,x int = 1,2;
	*(&x) = y;
	print x,y;
	var chk int = 100;
	var chk1 *int = &chk;
	print *chk1;
};