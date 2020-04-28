
import java.util.Scanner;
public class Student25 {
	public static void main(String[] args) {
		
		Scanner in = new Scanner(System.in);
		
		System.out.print("What is the temperature in Fahrenheit? ");;
		int farhen = in.nextInt();
		
		in.close();
		
		System.out.printf("It is currently %.2f\n", (float)(farhen - 32 * 5 / 9), "degrees Celsius");

	}

}
