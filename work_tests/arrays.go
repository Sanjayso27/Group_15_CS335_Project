package main;

func main() {
	var a[5] int;
	a[4] = 100;

	print a[4];

	var twoD [2][3]int;
    for i := 0; i < 2; i++ {
        for j := 0; j < 3; j++ {
            twoD[i][j] = i + j;
        };
    };
	print twoD[0][1];// 1

	print twoD[1][1]; // 2

	var threeD [2][1][3]int;
	for i := 0; i < 2; i++ {
        for j := 0; j < 1; j++ {
			for k:=0;k<3; k++ {
            	threeD[i][j][k] = i + j+k;
			};
        };
    };
	print threeD[1][0][2]; // 3
};