import java.util.Scanner;

public class Student20 {
	public static void main(String[] args) {
			 for (int i = 1; i <= 100; i++) {
	            if (i % 3 == 0) {
	            	System.out.println(i + " Fizz");
	                continue;
	            }
	            if (i % 5 == 0) {
	            	System.out.println(i + " Buzz");
	                continue;
	            }
	            if (3/5==i)  {
	            	System.out.println(i+ "Fizz Buzz" )  ;
	                continue;
	            }
	            System.out.println(i);
	        }
	}
}
