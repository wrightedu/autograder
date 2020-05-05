import java.util.Scanner;
public class Student03
{

	public static void main(String[] args)
	{
		/*
		Write a program that increments or decrements a value from 1. This program should take user
		input for the amount you want to increment a value by and the number of times you want to
		increment this number. The program should then output each step of this addition until it has
		incremented the number of times specified.
		*/
		Scanner keyboard = new Scanner(System.in);
		
		// increment/decrement value
		System.out.println("What value do you want to increment or decrement by? ");
		int incDec = keyboard.nextInt();
		// how many times?
		System.out.println("How many times would you like to increment or decrement? ");
		int amount = keyboard.nextInt();
		

		int i = 1;
		if(incDec > 0)
		{
			do
			{
				i+=incDec;
				System.out.println(i);
			}
			while(i <= (amount*incDec)-incDec);
		}
		else
		{
			do
			{
				i+=incDec;
				System.out.println(i);
			}
			while(i > 1+((amount-1)*incDec));
		}
		System.out.println("Final value: " + (i+incDec));
		

	}

}
