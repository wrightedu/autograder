import java.util.Scanner;

public class Student17 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

	System.out.println("What is the temperature in Fahrenheit? ");
	Scanner in = new Scanner(System.in);
	double F = in.nextDouble();
	in.close();
	
	double C = ((F-32)*(5.0/9.0));
	
	System.out.printf("It is currently %.2f degrees Celsius.", C);
	
	}

}
