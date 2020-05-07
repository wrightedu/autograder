
public class Student17 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
			
		int var = 0;
		do {
			var++;
			if (var%3==0 && var%5==0) {
				System.out.println(var + " fizz buzz");
			}else {
				if (var%3==0) {
					System.out.println(var + " fizz");
				}else if (var%5==0) {
					System.out.println(var + " buzz");
				}else {
					System.out.println(var);
				}
			}
		}while(var<100);
	}

}
