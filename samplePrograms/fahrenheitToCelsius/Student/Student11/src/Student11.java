import java.util.Scanner;

public class Student11 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

		Scanner input = new Scanner(System.in);
		double c;
		System.out.print("What is the temperature in Fahrenheit? ");
		float temp = input.nextInt();
		input.close();
		
		c = (temp - 32.00) * (5.00 /9.00); 
		System.out.printf("It is currently %.2f degrees Celsius." , c  );
		
	}

}
