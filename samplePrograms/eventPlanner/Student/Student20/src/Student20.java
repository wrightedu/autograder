import java.util.Scanner;

public class Student20 {

	public static void main(String[] args) 
	{
		Scanner input = new Scanner(System.in);
		System.out.print("How many people were invited to this event? ");
		int peopleInvited = input.nextInt();
		System.out.print("How many guests will they bring? ");
		int guestExtras = input.nextInt();
		int totalPeople = peopleInvited + (peopleInvited * guestExtras);
		double totalTables = Math.ceil(totalPeople / 6.0);
		System.out.printf("%.0f tables will need to be set up for this event.", totalTables);
	}

}
