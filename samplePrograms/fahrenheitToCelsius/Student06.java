import java.util.Scanner;

public class Student06 {

	public static void main(String[] args)
	{
		System.out.print("What is the temperature in Fahrenheit? ");
		Scanner input = new Scanner(System.in);
		double fahrenheit = input.nextInt();
		double celsius = ((fahrenheit - 32) * (5.0/9.0));
		System.out.println("It is currently " + celsius + " degrees Celsius.");
	
	}

}
