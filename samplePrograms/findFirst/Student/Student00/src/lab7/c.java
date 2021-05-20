package lab7;

import java.util.Scanner;

public class c {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

		
		Scanner input = new Scanner(System.in);
		int index = 0;
		int[] a = new int[10];
		
		System.out.print("Enter ten values, separated by spaces: ");
		for(int i = 0; i < 10; i++) {
			a[i] = input.nextInt();
		}
		System.out.print("Enter the number to find: ");
		int d = input.nextInt();
		for(int j = 0; j < a.length; j++) {
			if(a[j] == d) {
				index = j;
				
			}
		}
		System.out.print("your index is: " + index);
		
	}

}
