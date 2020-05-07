import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner in = new Scanner(System.in);
		System.out.print("Enter ten values, separated by spaces: ");
		int[] arr = new int[10];
		for (int i=0; i<arr.length; i++)
		{
			arr[i] = in.nextInt();
		}
		System.out.print("Enter the number to find: ");
		int num = in.nextInt();
		boolean here = false;
		int i;
		for (i=0; i<arr.length; i++)
		{
			if (num == arr[i])
			{
				here = true;
				break;
			}
		}
			if (here)
			{
				System.out.println("Your number is at index " + i);
			}
			else
			{
				System.out.println("Your number is at index -1");
			}
			in.close();
	}

}
