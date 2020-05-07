import java.util.Scanner;

public class Student05 {


	public static void main(String[] args) {
		// TODO Auto-generated method stub

		Scanner input = new Scanner(System.in);
		
		
		int i = 1;
		
		for(i = 1; i <= 100; i++ ) {
	
			
			System.out.print(i);
			
			if(i % 3 == 0) {
				System.out.print(" fizz");
				
			}
			if(i % 5 == 0) {
				System.out.print(" buzz");
			}
			
			
			System.out.println("");
		}
	
		
	
	
	}
}
