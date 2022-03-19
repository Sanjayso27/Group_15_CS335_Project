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
    r := rect{width: 10, height: 5};
    b := r.width + r.perim();
    i := 2;
    if i>0 {
        i++;
    }
    for i > 0 {
        i--;
        fmt.Println(b);
    }
    fmt.Println("area: ", r.area());
    fmt.Println("perim:", r.perim());

    rp := &r;
    fmt.Println("area: ", rp.area());
    fmt.Println("perim:", rp.perim());
}