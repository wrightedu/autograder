import java.util.Scanner;

// Week 2 Quiz: Temperature Converter

public class Student00 {

	public static void main(String[] args) {

Scanner in = new Scanner(System.in);
System.out.print("What is the temperature in Fahrenheit? ");
double temp = in.nextDouble();
in.close();
	
double finalTemp = (temp - 32) * (5.0 / 9.0);

System.out.printf("It is currently %.2f degrees Celsius.",finalTemp);

}
}
