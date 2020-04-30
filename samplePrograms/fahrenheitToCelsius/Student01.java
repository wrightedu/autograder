import java.util.Scanner;
import java.math.BigDecimal;

public class Student01 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		double f,result;
		Scanner ch = new Scanner(System.in);

		System.out.println("enter temperature in farnheit :");
		
		f=ch.nextDouble();
		
		firstclass adds=new firstclass();
		result=adds.calculatecelcius(f);
		System.out.println("result :"+result);
		
		}

}

class firstclass{

	public firstclass() {}
	public double calculatecelcius(double f){
		return(((f-32)*5)/9);
		
	}

}