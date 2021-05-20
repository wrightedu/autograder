import java.util.Scanner;
public class Student13 {

	public static void main(String[] args) 
	{
		//Set up Scanner?
		Scanner Temperature = new Scanner(System.in);
		//Get temperature in Fahrenheit from user
		System.out.println("What is the temperature in Fahrenheit? ");
		double Fahr = Temperature.nextDouble();
		
		//Clear the buffer
		Temperature.nextLine();
		
		//Convert to Celsius and display
		double Celsius = (Fahr - 32.0) * (5.0/9.0);
		System.out.println("It is currently, in Celsius: " + Celsius);
		
	}

}
