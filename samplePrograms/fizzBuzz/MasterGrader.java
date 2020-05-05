public class MasterGrader {
    public static void main(String[] args) {
        for(int i = 1; i < 101; ++i) {
            System.out.printf("%d ", i);
            if(i % 3 == 0) System.out.print("fizz ");
            if(i % 5 == 0) System.out.print("buzz");
            System.out.println();
        }
    }
}