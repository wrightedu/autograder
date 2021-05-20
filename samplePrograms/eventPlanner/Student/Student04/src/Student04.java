import java.util.Scanner;
public class Student04 {

	public static void main(String[] args) 
	{
		//Each person invited may bring people with them. Each table has a max of 6 people.
		
		Scanner in = new Scanner(System.in);
		
		System.out.print("How many people will be invited to this event? ");
		int invited = in.nextInt();
		
		System.out.print("How many people will they bring? ");
		int brought = invited * in.nextInt();
		
		int total = invited + brought;
		
		double needed = total / 6.0;
		
		System.out.printf((int) Math.ceil(needed) + " tables will need to be set up for the event");
		
		
		
	}

}
