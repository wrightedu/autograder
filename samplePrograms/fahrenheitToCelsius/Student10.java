import java.util.Scanner;

public class Student10 {

	public static void main(String[] args) {
		Scanner in = new Scanner (System.in);
		System.out.print("What is the temperature in Fahrenheit?");
		float myFloat = in.nextFloat();
		double temp = (myFloat - 32) * 5/9;
		System.out.println("It is currently " + temp);
		in.close();

	}

}
