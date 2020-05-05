
public class Student21 {

	public static void main(String[] args) {
		
		for (int i = 1; i < 101; i++) {
			System.out.print(i);
			
			if(i%3==0 && i%5==0) {
				System.out.print("fizz buzz\n");
			}
			else if(i%3==0){
				System.out.print("fizz\n");
			}
			else if(i%5==0){
				System.out.print("buzz\n");
			}
			else {
				System.out.print("\n");
			}
			
			
			
		}
		

	}

}
