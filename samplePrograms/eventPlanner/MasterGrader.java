import java.util.Scanner;

public class MasterGrader {
    public static void main(String[] args) {
        Scanner stdin = new Scanner(System.in);

        System.out.print("How many people will be invited to this event? ");
        int numPeople = stdin.nextInt();

        System.out.print("How many guests will they bring? ");
        int numGuests = stdin.nextInt();

        int totalPeople = numPeople + numGuests * numPeople;

        int tablesNeeded = totalPeople / 6 + (totalPeople % 6 != 0 ? 1 : 0);

        System.out.printf("%d tables will need to be set up for the event.%n", tablesNeeded);

        stdin.close();
    }
}