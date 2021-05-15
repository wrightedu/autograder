
import java.util.Scanner;

public class Student15 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

		Scanner in = new Scanner(System.in);
		//This is the scanner code for how many people will be invited to the event
		System.out.print("How many people will be invite to this event?");
		double People = in.nextDouble();
		
		//This is teh scanner code for how many people are invited to the event
		System.out.print("How many guests will they bring?");
		double Guest = in.nextDouble();
		
		//this will multiply the amount of people against the guests then add the people that were not counted 
		double amntpeople = ((People * Guest) + People);
		
		// this is declaring how many people per table 
		double Table = 6;
		
		// this is how many people per table without the math ceiling 
		double per_tbl = amntpeople / Table;
		
		//This is the final amount of tables you will need 
		int final_table = (int) Math.ceil(per_tbl);
		
		System.out.print(final_table + " tables will need to be set up for the event.");
		
	}
	
	
	

}
