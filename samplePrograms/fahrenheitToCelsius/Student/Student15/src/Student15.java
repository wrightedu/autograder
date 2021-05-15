import java.util.Scanner;

public class Student15 {

	public static void main(String[] args) {
		
		Scanner in = new Scanner(System.in);
		System.out.print("What is the temperature in Fahrenheit? ");

		double cel = (in.nextDouble()-32.0) * (5.0/9.0);
		System.out.printf("It is currently %.2f degrees Celsius.", cel);
		
		in.close();
	}
}
