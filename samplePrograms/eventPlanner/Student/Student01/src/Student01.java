


import java.util.Scanner;

public class Student01 {

	/**
	 * %.1f\n
	 */
	public static void main(String[] args) {
	
		Scanner kbreader = new Scanner(System.in);
		System.out.println("How many people will be invited to this event? ");
		double people = kbreader.nextInt();
		System.out.println ("How many guests will they bring? ");
		double guests = kbreader.nextInt();
		double tables = Math.ceil((people + (guests * people))/ 6);
		System.out.println(tables + " tables will be needed to be set up for this event");
		kbreader.close();

	}

}
