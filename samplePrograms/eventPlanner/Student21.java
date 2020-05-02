import java.util.Scanner;

public class Student21 {

	public static void main(String[] args) {
		Scanner in = new Scanner(System.in);
		System.out.print("How many people will be invited to this event? ");
		double guests = in.nextInt();
		System.out.print("How many guests will they bring? ");
		double plusOnes = in.nextInt();
		in.close();
		double tables =(guests * plusOnes) / 6;
		tables = Math.ceil(tables);
		System.out.printf("%.0f tables will be need to be set up for the event.", tables);
		
	}

}
