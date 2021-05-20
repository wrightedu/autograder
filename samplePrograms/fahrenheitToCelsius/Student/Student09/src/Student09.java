
import java.util.Scanner;

public class Student09 {
	public static void main (String[] args) {
		Scanner in = new Scanner(System.in);
		System.out.println("What is the temperature in Fahrenheit?");
		int fahren = in.nextInt();
		double cel = (fahren - 32) * (5.00/9.00);
		System.out.printf("It is currently %.2f", cel);
		System.out.print(" degrees Celsius.");
		
	}

}
