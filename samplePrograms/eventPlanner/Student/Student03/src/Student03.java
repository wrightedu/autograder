/**
 * 
 */
import java.util.Scanner;

public class Student03 {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		Scanner input = new Scanner(System.in);
		
		//asking user how many people were invited and storing in invited variable
		System.out.println("How many people will be invited to this event?");
		int invited = input.nextInt();
		
		//asking user how may guests invited people will bring and storing in guests variable
		System.out.println("How many guests will they bring?");
		int guests = input.nextInt();
		
		//closing input
		input.close();
		
		//computing total number of people going to event 
		int totalPeople = (invited * guests);
	
		//computing total number of people, using math.ciel to round up
		int tables = (int)Math.ceil((double)totalPeople/ 6.0);
		
		//printing out how many tables are needed
		System.out.println(tables +" tables will need to be set up for the event.");
	}

}
