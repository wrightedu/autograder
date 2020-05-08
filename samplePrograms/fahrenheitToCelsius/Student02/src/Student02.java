import java.util.Scanner;

public class Student02 {

	public static void main(String[] args) 
	{
		Scanner keyboard = new Scanner(System.in);
		System.out.println("What is the temperature in Fahrenheit? ");
		double tempF = keyboard.nextInt();
		double tempC = (tempF-32)*5/9;
		double tempCRounded = Math.round(tempC*100.00)/100.00;
		System.out.println("It is currently "+tempCRounded+ " degrees Celcius.");
		
	}

}
