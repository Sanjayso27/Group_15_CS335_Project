package main;

type hello struct {
	// c float;
	b int;
	a int;
};

type list struct {
	val int;
	next *list;
};

type hello_comp struct {
	b int;
	a int;
	d hello;
};

func main(){
    var k,l hello;
	k.a=1;
	k.b=3;
    print k.a,k.b;
	l = k; 
	print l.b;
	var t hello;
	t.a =1;
	t.b = 2;
	var x hello_comp;
	x.d = t;
	print x.d.b;
	var temp1 list;
	temp1.val =1;
	var temp2 list;
	temp2.val =2;
	temp2.next= &temp1;
	print (*(temp2.next)).val;
};