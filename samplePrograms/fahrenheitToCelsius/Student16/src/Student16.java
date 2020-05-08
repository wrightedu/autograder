
import java.util.Scanner;

public class Student16
{

	public static void main(String[] args)
	{
		// C = (f-32)*(5/9)
		Scanner keyboard = new Scanner(System.in);
		System.out.println("What is the temperature in Fahrenheit? ");
		double F = keyboard.nextDouble();
		
		double Cel = (F-32)*(5.0/9);
		
		System.out.println("It is curently " + Cel + " degrees Celcius.");
		

	}

}
