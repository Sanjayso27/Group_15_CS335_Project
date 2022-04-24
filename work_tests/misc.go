package main;

type hello struct {
	// c float;
	b int;
	a int;
};
// struct as param and return
func fun(temp hello) hello{
	if (temp.b*temp.b) > (temp.a){
		var chk hello;
		chk.a=10;
		chk.b=1;
		return chk;
	} else {
		var chk hello;
		chk.a=2;
		chk.b=2;
		return chk;
	};
};

//pointer as arg/return
func fun(ptr *int) *int{
	*ptr = 1;
	return ptr;
};

func main(){
	var x hello;
	x.b =2;
	x.a =1;
	var y hello = fun(x);
	print y.a;
	var t int =0;
	var u *int =fun(&t);
	print *u;
};