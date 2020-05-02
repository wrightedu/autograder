import java.util.Scanner;
public class Student22 {

	public static void main(String[] args) {
		
		Scanner in = new Scanner(System.in);
		
		System.out.print("How many people will be invitd to this event? ");
		double peopleinv = in.nextInt();
		System.out.print("How many guests will they bring? ");
		double extrap = in.nextInt();
		
		double tables = (peopleinv * extrap) / 6;
		double ceil = Math.ceil(tables);
		System.out.print( ceil + " tables will need to be set up for the event.");
		
		
		
		
	}

}
