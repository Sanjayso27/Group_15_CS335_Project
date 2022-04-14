package main

import "fmt";

type rectangle struct {
   length int;
   breadth int;
} ;

func main() {
   /* local variable definition */
   var a int = 10;
   if a == 15 {
      /* skip the iteration */
      a = a + 1;
      goto LOOP;
   }
   
   fmt.Printf("value of a: %d\n", a);
   a++;

   /* do loop execution */
   for a < 20 {
           
   }
}
