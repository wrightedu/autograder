import java.util.Scanner;

public class Student20 {
	public static void main(String[] args) {
		float temp;
		
		Scanner in = new Scanner(System.in);
		System.out.println("What is the temperature in Faharenheit? ");
		temp = in.nextInt();
		temp = (temp - 32)*5/9;
		System.out.println("It is currently "+temp+ " degrees Celsius" );
				
		
	}

}
