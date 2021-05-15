import java.util.Scanner;

public class Student13
{

	public static void main(String[] args)
	{
		//prompt user for # ppl invited to a social even and the # of guests those individuals will bring
		// output # tables needed. tables seat 6 people
		
		// invited * xtra guests
		// total / ceil of 6
		
		Scanner Keyboard = new Scanner(System.in);
		
		System.out.print("How many people will be invited to this event? ");
		int invitedGuests = Keyboard.nextInt();
		
		System.out.println("How many guests will they bring? ");
		int broughtGuests = Keyboard.nextInt();
		
		int totalGuests = broughtGuests * invitedGuests;
		double tables = totalGuests / 6.0;
		
		tables = Math.ceil(tables);
		
		System.out.println((int)tables + " tables will need to be set up for the event.");
	}

}
