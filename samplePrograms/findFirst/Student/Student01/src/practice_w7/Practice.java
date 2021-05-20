package practice_w7;

import java.util.Scanner;

public class Practice {

	public static void main(String[] args) {
		Scanner in = new Scanner(System.in);
		System.out.print("Enter 10 numbers separated by spaces: ");
		int[] array = new int[10];
		for(int i = 0; i<10; i++) {
			array[i] = in.nextInt();
		}
		System.out.print("Enter a number to find: ");
		int n = in.nextInt();
		int pos = -1;
		for(int i = 0; i<10; i++) {
			if(array[i] == n)
				pos = i;
		}
		System.out.println("Your number is at index " + pos);
		in.close();
	}

}
