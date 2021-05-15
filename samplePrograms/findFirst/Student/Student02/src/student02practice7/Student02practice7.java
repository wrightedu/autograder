package student02practice7;
import java.util.Scanner;

public class Student02practice7 {

    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        int[] arr = new int[10];
        System.out.println("Enter ten values, separated by spaces: ");
        for(int i=0; i<10; i++) {
            arr[i]=in.nextInt();
        }
       
        System.out.println("Enter the number to find: ");
        int n = in.nextInt();
        for (int j=0; j<arr.length; j++) {
            if(arr[j] == n) {
                System.out.println("Your number is at index " + j);
                break;
            } else if (n != arr[0] && n != arr[1] && n != arr[2] && n != arr[3]
            		&& n != arr[4] && n != arr[5] && n != arr[6] && n != arr[7]
            				&& n != arr[8] && n != arr[9]) {
            	System.out.println("Your number is at index -1");
            	break;
            }
        } 
        in.close();
       
    }

}