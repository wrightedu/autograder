import java.util.Scanner;
public class Student09 {


	public static void main(String[] args)
	{
		Scanner keyboard = new Scanner(System.in);
		
		System.out.print("How many people will be invited to this event:");
		double invited = keyboard.nextInt();
		System.out.print("How many guests will they bring:");
		double guests = keyboard.nextInt();
		System.out.print("If six people can sit at a table, the amount of tables needed will be:"+ (int)Math.ceil((invited*guests)/6));


		
		
		
		
		
		

	}

}
