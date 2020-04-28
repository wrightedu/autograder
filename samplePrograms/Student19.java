import java.util.Scanner;

public class Student19 {

	public static void main(String[] args) {
	Scanner f = new Scanner (System.in);
	System.out.print("What is the Temperature in Fahrenheit? ");
	double degreefahrenheit = f.nextDouble();
	double celcius = (degreefahrenheit-32)*(5.0/9);
	System.out.println("The temperature in celcius is "  + "degrees Celcius " + celcius);
	}

}
