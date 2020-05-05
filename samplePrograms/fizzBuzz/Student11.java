

public class Student11 
{

	public static void main(String[] args) 
	{
		
		for(int i = 0; i < 101; i++)
		{
			System.out.print(i);
			if(i % 3 == 0 && i % 5 ==0)
			{
				System.out.print(" fizz buzz");
			}
			else if(i % 3 == 0)
			{
				System.out.print(" fizz");
			}
			else if(i % 5 ==0)
			{
				System.out.print(" buzz");
			}
			else{}
			System.out.println();
		}
	}

}
