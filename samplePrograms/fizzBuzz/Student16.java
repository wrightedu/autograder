
public class Student16 {

	public static void main(String[] args) {
	
	
		
		for(int i= 1; i <= 100; i++)
		{	
			if (i%3 == 0 && i%5==0)
			{
			System.out.println(i +" fizz buzz");
			}
			else if(i%5 == 0)
			{
			System.out.println(i +" buzz");
			}
			else if(i%3==0) 
			{
			System.out.println(i+" fizz");
			}
			else
			System.out.println(i);
		}
	
		
		}

	}

