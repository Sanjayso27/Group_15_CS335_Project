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

const a, a = 1, 2;

func main() {
    //r := rect{10, 5};
    var a, b int = 2, 3;
    
    fmt.Println("area: ", r.area(), b);
    fmt.Println("perim:", r.perim());

    rp := &r;
    fmt.Println("area: ", rp.area());
    fmt.Println("perim:", rp.perim());
}