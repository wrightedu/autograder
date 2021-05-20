import java.util.Scanner;
public class Student21 {

	public static void main(String[] args) {
		Scanner input = new Scanner(System.in);
		
		System.out.print("What is the temperature in Fahrenheit? ");
		double F = input.nextDouble();
		
		double C = F - 32;
		System.out.print("It is currently " + (C*5/9) + " degrees Celsius");
	}

}
