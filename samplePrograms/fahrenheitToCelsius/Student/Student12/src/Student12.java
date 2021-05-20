import java.util.Scanner;
public class Student12
{
	public static void main(String[] args) {
		
	Scanner keyboard = new Scanner(System.in);
	System.out.print("What is the temperature in Fahrenheit:");
	double fahrenheit = keyboard.nextDouble();
	
	double celsius = (((fahrenheit-32)*5)/9);
	
	System.out.println("The temperature in Celcius is: " + celsius);
		

	}

}
