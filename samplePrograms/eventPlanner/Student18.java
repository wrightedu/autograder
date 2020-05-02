

import java.util.Scanner;

public class Student18 {

	public static void main(String[] args) {
		Scanner in = new Scanner(System.in);
		System.out.print("How many people will be invited to the event? ");
		int invited = in.nextInt();
		System.out.print("How many guests will they bring? ");
		int guests = in.nextInt();
		int people = invited * guests + invited;
		System.out.print((int) Math.ceil(people/6.0) + " tables will need to be set up for the event.");
		in.close();
	}

}
