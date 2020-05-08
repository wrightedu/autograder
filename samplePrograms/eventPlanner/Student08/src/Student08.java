

import java.util.Scanner;

public class Student08 
{

	public static void main(String[] args) 
	{
		Scanner keyboard = new Scanner(System.in);
		System.out.printf("How many people will be invited to this event? ");
		int invites = keyboard.nextInt();
		System.out.printf("How many guests will they bring? ");
		int guests = keyboard.nextInt();
		double tables = (guests + 1) * invites / 6;
		System.out.println(Math.ceil(tables) + " tables will need to be set up for the event.");

	}

}
