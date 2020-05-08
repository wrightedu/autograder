import java.util.Scanner;
public class Student04 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		
	
	// C = (F-32) * (5/9)
	Scanner in = new Scanner(System.in);
	System.out.println("What is the temperature in Farenheit?");
	double temperature = in.nextDouble();
	in.close();
	double value = 5/9.0;
	double cTemp = (temperature - 32)*(value);

	
	System.out.println("It is currently " + cTemp + " degrees Celsius.");
	
		
		
		
		
		
		
		
		
		
		
		
	}

}
