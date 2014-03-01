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

		//Compile the java file
		compileJava( sessionID );

		//Execute the file
		executeJava( sessionID );
	}

	/**
	 * Executes a shell command prints the output to System.out and 
	 */
	private static void executeShellCommand( String command,
			String destinationFile ) {
		Runtime runtime = Runtime.getRuntime();
		File file = new File( destinationFile );
		Process p;

		try {
			//Create the destination file
			if( ! file.exists() ) {
				file.createNewFile();
			}
			
			//Create the execution process
			p = Runtime.getRuntime().exec( command );
			p.waitFor();

			//Get the the output stream from the process
			BufferedReader reader = new BufferedReader( 
					new InputStreamReader( p.getInputStream() ) );

			//Open the file writer
			FileWriter writer = new FileWriter( file );

			//Print and write the data to file
			String line = "";
			while( (line = reader.readLine()) != null ) {
				System.out.println( "Code executed: " + line);
				writer.write( line + "\n" );
			}

			writer.close();
		}
		catch( IOException ioe ) {
			System.out.println( "In JavaFiddleUtils.executeShellCommand:" );
			ioe.printStackTrace();
		}
		catch( InterruptedException ie ) {
			System.out.println( "In JavaFiddleUtils.executeShellCommand:" );
			ie.printStackTrace();
		}
	}
	
	/**
	 * 
	 */
	private static void convertSnippets( String sessionID ) {
		try {
			File destinationFile = new File( sessionID + ".java" );

			//Create the file if it does not exist
			if( ! destinationFile.exists() ) {
				throw new RuntimeException( "sessionID source file does not " + 
						"exist!" );
			}
			
			Scanner fileScan = new Scanner( destinationFile );

			//Read in the file 
			StringBuilder sb = new StringBuilder();

			while( fileScan.hasNextLine() )
				sb.append( fileScan.nextLine() + "\n" );

			String snippet = sb.toString();

			/* Rewrite to the source file */
			FileWriter writer = new FileWriter( destinationFile );
			
			//Write the file header and main function
			String name = removeDirectories(sessionID);
			writer.write( "public class " + name + " {\n" );
			writer.write( "public static void main( String[] args ) {\n" );
			
			//Write the snippet
			writer.write( snippet );

			//Write the ending brackets and close the writer
			writer.write( "}\n}" );
			writer.close();
		}
		catch( IOException ioe ) {
			System.out.println( "In JavaFiddleUtils.convertSnippets:" );
			ioe.printStackTrace();
		}
	}
	
	/**
	 * Compiles the java file and outputs it to a file named
	 * sourceFileName.class
	 *
	 * @param sourceFileName The name of the file that is being compiled
	 */
	private static void compileJava( String sourceFileName ) {
		String javacCommand = "javac " + sourceFileName + ".java";
		executeShellCommand( javacCommand, sourceFileName + ".comp.out" );
	}

	/**
	 * Executes the java file and outputs it to a file
	 */
	private static void executeJava( String sourceFileName ) {
		String name = removeDirectories(sourceFileName);
		String javaCommand = "java -classpath tmp/ " + name + " > " + 
			sourceFileName + ".output.txt";
		executeShellCommand( javaCommand, sourceFileName + ".out.txt" );
	}

	private static String removeDirectories( String name ) {
		for(int i= name.length()-1; i>0; i--){
			if(name.charAt(i)==('/')){
				name = name.substring(i+1, name.length());
				return name;
			}
		}
		return name;
	}
}
