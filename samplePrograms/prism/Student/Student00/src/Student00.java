/*
 * TODO Your name goes here
 * TODO Project description goes here
 */
import java.util.Scanner;

public class Student00 {
    public static void main(String[] args) {
        Scanner stdin = new Scanner(System.in);
        
        System.out.print("What is the length? ");
        double length = (int)stdin.nextDouble();
        
        System.out.print("What is the width? ");
        double width = (int)stdin.nextDouble();
        
        System.out.print("What is the height? ");
        double height = (int)stdin.nextDouble();
        
        double volume = length * width * height;
        double surfaceArea = 2 * (length * width + length * height + width * height);
        
        System.out.printf("A %.2f x %.2f x %.2f prism has:%n", length, width, height);
        System.out.printf("  - A volume of %.2f units^3%n", volume);
        System.out.printf("  - A surface area of %.2f units^2%n", surfaceArea);
    }
}