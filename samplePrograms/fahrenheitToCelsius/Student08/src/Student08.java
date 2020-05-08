import java.util.Scanner;
public class Student08 {

	public static void main(String[] args) {
		

		Scanner in = new Scanner(System.in);
		
		System.out.print("Please Enter Fahrenheit temperature: ");
		
		Double Fahrenheit = in.nextDouble();
		
		double Convert = ((Fahrenheit - 32) / (5/9));
		
		System.out.printf("It is currently ", Convert);
		
	}

}
