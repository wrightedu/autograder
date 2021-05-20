import java.util.Scanner;

public class Student06 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

		
		
		Scanner in = new Scanner(System.in);
		System.out.println("How many people will be invited to the event? ");
		int invites = in.nextInt();
		System.out.println("How many guests will they bring? ");
		int guests = in.nextInt();
		in.close();
		double neededTables =  ((invites * guests) + invites) / 6;
		
		System.out.println(Math.ceil(neededTables) + " tables will need to be set up before this event.");
		
	}

}
