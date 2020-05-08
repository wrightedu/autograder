
import java.util.Scanner;
public class Student11 {
	public static void main(String[] args) {
		
		Scanner in = new Scanner(System.in);
		System.out.print("How many people will be invited to this event?" );
		int people = in.nextInt();
		System.out.print("How many guests will they bring? ");
		int guest = in.nextInt();
		in.close();
		
		int table = people * guest;
		int numTable = table / 6;
		
		System.out.print((int)Math.ceil(numTable) + " tables will need to be set up for the event.");
	}

}
