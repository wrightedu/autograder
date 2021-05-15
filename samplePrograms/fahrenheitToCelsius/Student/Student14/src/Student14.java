import java.util.Scanner;

public class Student14 
{

	public static void main(String[] args) 
	{
		
		Scanner temperature = new Scanner(System.in);
		System.out.print("What is the temperature in Fahrenheit: ");
		double input1 = temperature.nextDouble();
		System.out.print("It is currently " + (input1 - 32)*(5/9.));
		System.out.print(" Celcius");
	}

}