


public class Student14 {
	
	public static void main(String[] args) {
		
		
		for (int i = 1; i <= 100; i++) {
			
			int isEven = i % 5;
			
			int isOdd = i % 3;
			
			if (isEven == 0) {
			
				System.out.println(i + " buzz");
				
			} else if (isOdd == 0) {
				System.out.println(i + " fizz");
			} else {
				System.out.println(i);
			}
			
		}
		
	}

}
