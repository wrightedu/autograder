import java.util.Scanner;

public class Student05 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
			
			System.out.print("How many people will be invited to this event? ");
			Scanner in = new Scanner (System.in) ;
			double people = in.nextDouble();
			System.out.print("How many guests will they bring?");
			double guests = in.nextDouble();
			double total = people * guests;
			double tables = (Math.ceil(total/6));
			System.out.println((int)tables + " tables will need to be set up for the event.");		
					
	}

}
