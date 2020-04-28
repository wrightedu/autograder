import java.util.Scanner;

public class Student03 {

	public static void main(String[] args) {
		// Creates Scanner
		Scanner in = new Scanner(System.in);
		// Prompts user for the temperature in Fahrenheit, user inputs
		System.out.print("What is the temperature in Fahrenheit? ");
		double tempF = in.nextDouble();
		// Converts from Fahrenheit to Celsius
		double tempC = (tempF-32) * 5/9;
		// Outputs the temperature in Celsius
		System.out.printf("It is currently %.2f degrees Celsius.", tempC);
		// Closes scanner
		in.close();
	}

}
