import java.util.Scanner;

public class Student22 {

	public static void main(String[] args) {
	
		Scanner in = new Scanner(System.in);
		
		System.out.println("What is the temperature in Fahrenheit? ");
		int t = in.nextInt();
		System.out.println("It is currently " + (t-32) * (5.0/9.0) + " degrees Celsius.");
		
		
		
		

	}

}
