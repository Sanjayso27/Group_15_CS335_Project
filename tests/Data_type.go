package main;

type hello struct {
	c float;
	a int;
	d *hello;
};

type hello_comp struct {
	b int;
	a int;
	d hello;
};

func main(){
    var b float;
    var a int;
    var k,l hello;
	var x hello_comp;
    a = k.a;
	b = k.c;
	// l = k; // why not working
};