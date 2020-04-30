import java.util.Scanner;

public class Student18 {
	public static void main(String[] args) {
		double F = 0.0,C = 0.0;
		Scanner kbreader = new Scanner(System.in);
		System.out.println("Input a Temperature in Fahrenheit: ");
		F = kbreader.nextDouble();
		C = (F - 32.0) * (5.0/9.0);
		 System.out.println("The Celsius Temperature is " + C);
		 
	}

}
 