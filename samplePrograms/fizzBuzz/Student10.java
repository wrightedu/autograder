public class Student10 
{
	public static void main(String[] args)
	{
		//increment 1 to 100 with divisibility
		int variable = 1;
		int looping = 0;
		while(looping != 100)
		{
			if(variable %3 == 0 && variable %5 ==0)
			{
				System.out.println(variable + " fizz buzz");
			}
			else if(variable %3 == 0)
			{
				System.out.println(variable + " fizz");
				
			}
			else if(variable %5 == 0)
			{
				System.out.println(variable + " buzz");
				
			}
			else
			{
				System.out.println(variable);
				
			}
			variable++;
			looping++;
			
		}
		
	}

}
