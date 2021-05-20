import java.util.Scanner;

public class Student19 {

	public static void main(String[] args) {
		
		Scanner in = new Scanner(System.in);
		
		System.out.println("How many people will be invited to this event? ");
		
		int p = in.nextInt();
		
		System.out.println("How many guest will they bring? ");
		
		int g = in.nextInt();
		
		double sits = 6;
		
		double tables = ((p * g)/sits);
		
		Math.ceil(tables);
		
		double rounded = Math.ceil(tables);
		
		System.out.printf( "%.0f tables will need to be set up for the event ", rounded);
		
		
		
	}

}
