import java.util.Scanner;

public class Student05 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

		System.out.println("What is the temperature in Fahrenheit? ");
		Scanner in = new Scanner(System.in);
		int userImput = in.nextInt();
		System.out.println("It is currently " + (userImput - 32) * (5/9.0) + " degrees Celsius.");
	}

}

