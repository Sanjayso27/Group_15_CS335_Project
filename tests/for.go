package main;

func main() {
	for i:=0;i<4;i++ {
		print "Hello",i;
	};
	var x int =4;
	for ;x>0;{
		x--;
	};
	for x=0;x<4;{
		x++;
	};
	for ;x>0;x--{
		print "working";
	};
	for n := 0; n <= 5; n++ {
        if (n%2) == 0 {
            continue;
        };
        if n>3 {
			break;
		};
    };
	count :=0;
	for i := 0; i < 2; i++ {
        for j := 0; j < 3; j++ {
            count += (i+j);
        };
    };
};