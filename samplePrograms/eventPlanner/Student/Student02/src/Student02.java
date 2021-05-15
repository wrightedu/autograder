import java.util.Scanner;

public class Student02 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
	

	// Lab 2: Event Planner

	Scanner in1 = new Scanner(System.in);
	System.out.print("How many people will be invited to this event? ");
	int people = in1.nextInt();
	System.out.print("How many guests will they bring? ");
	int guests = in1.nextInt();
	
	double tables = ((people * guests) / 6.0);
	System.out.printf("%.0f tables will need to  be set up for the event.\n",tables);
	
	in1.close();
	
	}
}
