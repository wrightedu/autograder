

import java.util.Scanner;

public class Student16 {

	public static void main(String[] args) {
		
	//-------------------USER INPUT SECTION-------------------------------------	
		Scanner people = new Scanner(System.in);
		System.out.print("How many people will be invited to this event? ");
		float numbPeople = people.nextInt();
		System.out.print("How many guests will they bring? ");
		float guests = people.nextInt();
		people.close();
	//-------------------------------------------------------------------------
		//----------CALCULATIONS-----------------------------------------------
		float Totalpeople = ((numbPeople) * (guests)) + (numbPeople); //Math reasoning: Number of guest said people will bring, plus the original people
		float tablesNeeded1 = (Totalpeople) / (6);
		double tablesNeeded = (Math.ceil(tablesNeeded1));
		//---------------------------------------------------------------------
	//--------------OUTPUT-----------------------------------------------------
		System.out.printf("%.0f",tablesNeeded);
		System.out.print(" tables will need to be set up for the event.");
	//-------------------------------------------------------------------------


	}

}
