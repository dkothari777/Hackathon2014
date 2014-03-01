import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.io.IOException;

import java.util.Scanner;

public class JavaFiddleUtils {

	public static void main( String[] args ) {
		//Read in the system arguments
		if( args.length < 1 ) {
				throw new RuntimeException("Requires a sessionID argument!");
		}

		String sessionID = args[0];

		//Conver the snippets a file in the format of <sessionID>.java
		convertSnippets( sessionID );
	}

	private static void convertSnippets( String sessionID ) {
		try {
			File destinationFile = new File( sessionID + ".java" );

			//Create the file if it does not exist
			if(!destinationFile.exists()) {
				throw new RuntimeException( sessionID + " sessionID source file does not " + 
						"exist!" );
			}
			
			Scanner fileScan = new Scanner(destinationFile);

			//Read in the file 
			StringBuilder sb = new StringBuilder();

			while( fileScan.hasNextLine() )
				sb.append( fileScan.nextLine() + "\n" );

			String snippet = sb.toString();

			System.out.println( "public class " + sessionID.substring(4) + " {\npublic static void main( String[] args ) {\n"+snippet+"}\n}");
		}
		catch( IOException ioe ) {
			System.out.println( "In JavaFiddleUtils.convertSnippets:" );
			ioe.printStackTrace();
		}
	}
}
