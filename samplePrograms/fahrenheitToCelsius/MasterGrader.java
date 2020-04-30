import java.util.Scanner;

public class MasterGrader {
    public static void main(String[] args) {
        Scanner stdin = new Scanner(System.in);

        System.out.print("What is the temperature in Fahrenheit? ");

        int tempf = stdin.nextInt();

        System.out.printf("It is currently %.2f degrees Celsius.%n", (tempf - 32) * 5.0 / 9.0);
    }
}