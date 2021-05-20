import java.util.Scanner;
public class Student10 
{
	public static void main(String[] args) 
	{
		//each table can only seat 6 people
		//everyone must have a place to sit
		Scanner keyboard = new Scanner(System.in);
		
		System.out.println("How many people will be invited to this event? ");
		int invited = keyboard.nextInt();
		System.out.println("How many geusts will they bring? ");
		int extraInvites = keyboard.nextInt();
		int totalGuests = invited * extraInvites;
		//round up to nearest whole
		double tables = (double)totalGuests/6*100;
		double tablesR = Math.ceil(tables/100);
		System.out.println((int)tablesR + " tables will need to be set up for this event.");
		keyboard.close();
	}
}
