import java.util.Scanner;

public class Student23 {
	public static void main(String[] args)	{
		
		System.out.print("What is the temperature in Farenheight: ");
		
		Scanner eyes = new Scanner(System.in);
		double faren = eyes.nextDouble();
		
		double newTemp;
		newTemp = (faren - 32) * 5/9;
		
		
		System.out.printf("The given temperature in Celsius is: %.2f degrees \n ", newTemp);
		eyes.close();
		
		
	}

}
