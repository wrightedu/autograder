
public class Student15 { // Testing ability to write loops

	public static void main(String[] args) { 
		// TODO Auto-generated method stub

        int i = 0; // Start integer at 0

        while (true) { // While function is true
            i++; // Increment i

            System.out.println(i); // Print i

            if (i % 3 == 0) { // If i is divisible by 3
            System.out.println(i + "fizz"); // Print i + fizz
            }
            	else if (i % 5 == 0) { // If i is divisible by 5
            System.out.println(i + "buzz"); // Print i + buzz
            	}
            	
            	else if (i % 15 == 0) { // If i is divisible by both 3 and 5
            System.out.println(i + "fizz buzz"); // Print i + fizz buzz
            	}
            
            if (i == 100) { // If i equals 100
                
                break; // Stops loop
                
        }
        
		
	}

	}
}
