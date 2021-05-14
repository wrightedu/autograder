import java.util.Scanner;

public class MasterGrader {
    public static void main(String[] args) {
        Scanner stdin = new Scanner(System.in);

        System.out.print("Enter ten values, separated by spaces: ");
        int[] numbers = new int[10];

        for(int i = 0; i < 10; ++i) {
            numbers[i] = stdin.nextInt();
        }

        System.out.print("Enter the number to find: ");
        int toFind = stdin.nextInt();

        int index = -1;

        for(int i = 0; i < 10; ++i) {
            if(numbers[i] == toFind) {
                index = i;
                break;
            }
        }

        System.out.printf("Your number is at index %d%n", index);
    }
}