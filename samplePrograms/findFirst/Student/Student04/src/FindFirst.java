import java.util.Scanner;

public class FindFirst {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

		Scanner in = new Scanner(System.in);
		System.out.println("Enter ten values, separated by spaces:");
		String input = in.nextLine(); 
		String[] numbers = input.split(" ");
		// 
		System.out.println("Enter the number to find: ");
		int numberToFind = in.nextInt();
		for(int i = 0; i < 10; i++) {
			if(Integer.parseInt(numbers[i]) == numberToFind) {
				System.out.println(i);
				break;
			}
			else if(Integer.parseInt(numbers[i]) != numberToFind && i == 9) {
				System.out.println("-1");
			}
		}
		
	}

}
