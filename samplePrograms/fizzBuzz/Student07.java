
public class Student07 {

	public static void main(String[] args) {
		int stopValue = 101;
		int x = 1;
		while (x!= stopValue)
		{
			if (x % 5 == 0 && x % 3 == 0)
			{
				System.out.println(x + " fizz buzz");
			}
			else if(x % 3 == 0)
			{
				System.out.println(x + " fizz");
			}
			else if(x % 5 == 0)
			{
				System.out.println(x + " buzz");
			}
			else 
			{
				System.out.println(x);
			}
			x++;
		}

	}

}
