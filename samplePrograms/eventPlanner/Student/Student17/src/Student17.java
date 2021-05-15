

import java.util.Scanner;

public class Student17 {

	public static void main(String[] args) {
		Scanner in = new Scanner(System.in);
		System.out.print("How many people will be invited to this event?" );
		float numberOfPeople = in.nextFloat();
		System.out.print("How many guest will they bring?" );
		float numberOfGuests = in.nextFloat();
		float numberOfTables = ((numberOfPeople * numberOfGuests) + numberOfPeople) / 6;
		float finalAnswer = (float) Math.ceil(numberOfTables);
		System.out.print("You will need " + finalAnswer + " tables");
		in.close();

	}

}
