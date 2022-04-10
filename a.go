
// Go program to illustrate the
// concept of the call by value
package main
  
import "fmt"
  
// function which modifies
// the value
func modify(Z int,) {
    Z = 70
}
  
// Main function
func main() {
  
    var Z int = 10
      
    fmt.Printf("Before Function Call, value of Z is = %d", Z)
  
    // call by value
    modify(Z)
      
    fmt.Printf("\nAfter Function Call, value of Z is = %d", Z)
}