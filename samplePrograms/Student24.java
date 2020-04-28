
import java.util.Scanner;
public class Student24 {
	public static void main(String[] args) {
		
		Scanner in = new Scanner(System.in);
		
		System.out.print("What is the temperature in Fahrenheit? ");;
		double farhen = in.nextDouble();
		
		in.close();
		
		System.out.printf("It is currently %.2f\n", ((farhen - 32) * 5 / 9), "degrees Celsius");

	}

}
