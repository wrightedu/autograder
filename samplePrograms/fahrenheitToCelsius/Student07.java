import java.util.Scanner;

public class Student07 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Scanner in = new Scanner(System.in);
		System.out.print("What is the temerature in Fahrenheit?");
		 double F = in.nextDouble();
		 double C = (F - 32);
		 double FinalTemp = C*.5555;
		 System.out.print("It is currently " + FinalTemp + " degrees Celsius");
		
	}

}
