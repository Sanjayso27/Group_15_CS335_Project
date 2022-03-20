package main

import "fmt";

type rect struct {
    width, height int;
};

func (r *rect) area() int {
    return r.width * r.height;
}

func (r rect) perim() int {
    return 2*r.width + 2*r.height;
}

func main() {
    //r := rect{10, 5};
    b := r.width + r.perim();
    i := 2;
    var i, j int = i, 3;
    if i>0 {
        i++;
    }
    k := make([]rect, 3);
    i, j := i+j, 3+2;
    for i,j := 2,1; i > 0; i-- {
        i--;
        j--;
        fmt.Println(b);
    }
    fmt.Println("area: ", r.area());
    fmt.Println("perim:", r.perim());

    rp := &r;
    fmt.Println("area: ", rp.area());
    fmt.Println("perim:", rp.perim());
}