import java.util.Scanner;
import java.lang.Math;

public class Student07 
{

	public static void main(String[] args) 
	{
		Scanner people = new Scanner(System.in);
		
		System.out.print("How many people will be invited to this event? ");
		int invited = people.nextInt();
		
		System.out.print("How many guests will they bring? ");
		int guests = people.nextInt();
		
		double tables = (invited * guests)/(6.0);
		
		System.out.print((int) Math.ceil(tables) +  " tables will need to be set up for the event");
	
	}

}
