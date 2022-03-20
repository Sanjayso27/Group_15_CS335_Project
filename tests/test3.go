for n <= 5 {

    var i int;
    for i <= 3 {
        //fmt.Println(i)
        i = i + 1;
    }
    var a [5]int = [5]int{1, 2, 3, 4, 5};
    fmt.Println("emp:", a);

    a[4] = 100;
    fmt.Println("set:", a);
    fmt.Println("get:", a[4]);

    fmt.Println("len:", len(a));
    function(a, b, c);

    j:=1;
    // for j := 7; j <= 9; j++ {
    //     j += 1;
    //     //fmt.Println(j)
    // }

    
    // for {
    //     //fmt.Println("loop")
    //     break;
    // }
    // for n := 0; n <= 5; n++ {
    //     if n%2 == 0 {
    //         continue;
    //     }
    // }
}