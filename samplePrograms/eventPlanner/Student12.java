
import java.util.Scanner;

public class Student12 {

	public static void main(String[] args) {
		
		Scanner pineapple = new Scanner (System.in);
		
		System.out.print("How Many people are invited this event? ");
		int invite = pineapple.nextInt();
		System.out.print("How Many guests are they bringing to this event? ");
		int guest = pineapple.nextInt();
		pineapple.close();
		
		int total = invite * guest;
		
		int tables = (int) (total / 6.0);
		
		int finalnum = (tables) + (tables%7)/(tables%7);

		
		System.out.printf("You will need %d tables", finalnum);
		
		
		
		
	}

}
