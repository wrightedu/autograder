import java.util.Scanner;

public class Student14 {

	public static void main(String[] args) {
	Scanner invit = new Scanner(System.in);
	System.out.print("Enter number of people invited ");
	double peopleInvit = invit.nextDouble();
	double guestNumber = 4;
	double totalNumberOfPeople = guestNumber * 10;
	double availableTable = totalNumberOfPeople/7.0;
	System.out.printf("The number of table needed to be set is %.1f/n': ",availableTable);
	

	}

}
