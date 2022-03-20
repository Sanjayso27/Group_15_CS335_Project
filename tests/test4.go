package main

import "fmt";

func main() {

    var a [5]int = [5]int{1, 2, 3, 4, 5};
    fmt.Println("emp:", a);

    a[4] = 100;
    fmt.Println("set:", a);
    fmt.Println("get:", a[4]);

    fmt.Println("len:", len(a));
    function(a, b, c);
    {
        {
            {
                LOOP : 
                i = 1;
                i, j := 1, 2;
                var twoD [2][3]int;
                if i := 0; i<0 {
                    for j := 0; j < 3; j++ {
                        twoD[i][j] = i + j;
                    }
                }
                fmt.Println("2d: ", twoD);
                a++;
            }
        }
    }
    i = 1;
    i, j := 1, 2;
    var twoD [2][3]int;
    for i := 0; i < 2; i++ {
        for j := 0; j < 3; j++ {
            twoD[i][j] = i + j;
        }
    }
    fmt.Println("2d: ", twoD);
}