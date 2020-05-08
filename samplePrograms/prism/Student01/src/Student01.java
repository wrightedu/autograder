import java.util.Scanner;

public class Student01 {
    public static void main(String[] args) {
        Scanner kbd = new Scanner(System.in);
	
	// Input
	System.out.println("This program will compute the volume and surface area of a rectangular prism");
    	System.out.print("Enter the prism's length: ");
	float length = kbd.nextFloat();
	System.out.print("Enter the prism's width: ");
	float width = kbd.nextFloat();
	System.out.print("Enter the prism's height: ");
	float height = kbd.nextFloat();

	// Calculations
	float volume = length * width * height;
	float surfaceArea = 2 * (width * length + length * height + height * width);

	// Output
	System.out.println("A prism with a length of " + Math.round(length * 100.0) / 100.0 + " units, a width of " + Math.round(width * 100.0) / 100.0 + " units, and a height of " + Math.round(height * 100.0) / 100.0 + " units has a volume of " + Math.round(volume * 100.0) / 100.0 + " units cubed and a surface area of " + Math.round(surfaceArea * 100.0) / 100.0 + " units squared.");
    }
}