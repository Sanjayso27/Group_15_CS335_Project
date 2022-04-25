package main;

func main() {
	var f0, f1 int = -1, 1;
	for i:=0; i<10; i++ {
		var tmp int = f1;
		f1 = f0 + f1;
		f0 = tmp;
		print f1;
	};
};
