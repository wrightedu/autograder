import java.util.Scanner;

public class Student02 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		
		
		
		
		for (int start = 1; start<= 100; start++ ) {
			if( start % 15 == 0) {
				System.out.println(start + " fizz buzz");
			}
			else if (start % 3 == 0) {
				System.out.println(start + " fizz");
			}
			else if (start % 5 == 0) {
				System.out.println(start + " buzz");
			}
			else {
				System.out.println(start);
			}
			
		}
		

	}

}
