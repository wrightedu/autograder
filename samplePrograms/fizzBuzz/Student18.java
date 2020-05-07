public class Student18 {

	public static void main(String[] args) {
		
		
		for (int TimeCount = 0; TimeCount <= 100; TimeCount++) {
			System.out.println(TimeCount);
		 if (TimeCount == TimeCount % 3) {
			 
			 System.out.print("fizz");
		 }
		 else if (TimeCount == TimeCount % 5) {
			 
			 System.out.print("Buzz");
		 }
		 else if (((TimeCount == TimeCount % 3) || (TimeCount == TimeCount % 5))) {
			 
			 System.out.print("FizzBuzz");
		 }
		
		
		
		

	}

}
}
