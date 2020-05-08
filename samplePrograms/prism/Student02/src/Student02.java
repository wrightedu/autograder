import java.util.Scanner;

public class Student02 {
    public static void main(String[] args) {
        Scanner stdin = new Scanner(System.in);

        System.out.println("This program will compute the volume and surface area of a rectangular prism");
        
        System.out.println("Enter the prism's length: "); 
        double length = stdin.nextDouble();
        
        System.out.println("Enter the prism's width: "); 
        double width = stdin.nextDouble();

        System.out.println("Enter the prism's height: "); 
        double height = stdin.nextDouble();

        double volume = length * width * height;
        double surfaceArea = 2 * (length * width + length * height + width * height);
        
        System.out.printf("A prism with a length of %.2f units, a width of %.2f units, and a height of %.2f units%n", length, width, height);
        System.out.printf("has a volume of %.2f units cubed and a surface area of %.2f units squared.%n", volume, surfaceArea);
    }
}