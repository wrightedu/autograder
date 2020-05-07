

/**
 * Program: Fizz Buzz
 * Purpose: To test ability to write loops
 * Directions: program that increments a variable from 1 - 100
 * output a variable every line
 * if divisible by 3 then output buzz
 * if divisible by 5 output buzz
 * if divisible by 3 and 5 it should output fizz buzz
 *
 */
//import java.util.Scanner;
public class Student09 {

	

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		//Scanner kbreader = new Scanner(System.in);
		
		for (int i = 1; i <= 100; i++) {
			
			if (i%3 == 0 && i%5 == 0) {
				System.out.println(i + " Fizz Buzz");
			}
			
			else if(i%3 == 0){
				System.out.println(i + " Fizz");
			}
			 
			else if(i%5 == 0){
				System.out.println(i + " Buzz");
			}
			else{
				System.out.println(i);
			}
			 
			}
	}

}

