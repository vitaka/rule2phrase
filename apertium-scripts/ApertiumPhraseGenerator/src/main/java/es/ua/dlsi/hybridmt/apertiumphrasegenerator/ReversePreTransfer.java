/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.io.Writer;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *
 * @author vmsanchez
 */
public class ReversePreTransfer {

    private List<ReplacementPattern> replacementPatterns;

    public ReversePreTransfer() {
        replacementPatterns=new LinkedList<ReplacementPattern>();
    }

    public void reverse(Reader in, Writer out)
    {
        reverse(in, out, true);
    }

    public void reverse(Reader in, Writer out, boolean generateAlignments)
    {
        BufferedReader reader=new BufferedReader(in);
        Pattern patternLexicalForm=Pattern.compile("(_vmsanchez_sep_(\\d+)_numwords_)?\\^");

        String line=null;

        try
        {
            //if(generateAlignments)
            //{
                while((line=reader.readLine())!=null)
                {
                    String additionalTransferAls=null;
                    if(generateAlignments)
                    {
                        String[] parts=line.split(" \\|\\|\\| ");
                        line=parts[0];
                        additionalTransferAls=parts[1];
                    }

                    StringBuilder builder=new StringBuilder(line);
                    //if(line.indexOf("+")>=0)
                    //{
                        for(ReplacementPattern rp: replacementPatterns)
                        {
                            Matcher m=rp.getPattern().matcher(line);
                            while(m.find())
                            {
                                if(generateAlignments)
                                {
                                    builder.replace(m.start(), m.end(), "_vmsanchez_sep_"+rp.getNumSourceWords()+"_numwords_"+rp.getReplacement());
                                }
                                else
                                {
                                    builder.replace(m.start(), m.end(), rp.getReplacement());
                                }

                                line=builder.toString();
                                m=rp.getPattern().matcher(line);

                                //debug
                                //System.err.println(builder.toString());
                            }
                        }

                    

                    if(generateAlignments)
                    {
                        StringBuilder alignments= new StringBuilder();
                        Matcher m=patternLexicalForm.matcher(builder.toString());
                        int offset=0;
                        int offsetChars=0;
                        int word=0;
                        while(m.find())
                        {
                            word++;
                            if(m.group(2)!=null)
                            {
                                for(int i=0; i<Integer.parseInt(m.group(2));i++)
                                    alignments.append(word).append("-").append(word+offset+i).append(" ");
                                offset+=(Integer.parseInt(m.group(2))-1);
                                builder.replace(m.start()-offsetChars, m.end()-offsetChars, "^");
                                offsetChars+=(m.group().length()-1);
                            }
                            else
                            {
                                alignments.append(word).append("-").append(word+offset).append(" ");
                            }
                            
                        }
                        out.write(builder.append(" ||| ").append(alignments).append(" ||| ").append(additionalTransferAls).append("\n").toString());
                    }
                    else
                         out.write(builder.append("\n").toString());
                    
                }
           /* }
            else
            {
                StringBuilder builder=new StringBuilder();
                
                while((line=reader.readLine())!=null)
                {
                    builder.append(line).append("\n");
                }

                String content=builder.toString();

                int numrp=0;
                for(ReplacementPattern rp: replacementPatterns)
                {
                    numrp++;
                    System.err.println("Applying replacement pattern "+numrp+" of "+replacementPatterns.size());
                    content=rp.getPattern().matcher(content).replaceAll(Matcher.quoteReplacement(rp.getReplacement()));
                }

                out.write(content);
            
            }*/

        }catch(Exception e)
        {
            e.printStackTrace();
        }

    }

    public void loadFromFile(File f)
    {
         String line;
        BufferedReader reader=null;
        try
        {
        reader=new BufferedReader(new InputStreamReader(new FileInputStream(f),Charset.forName("UTF-8") ));
            while((line=reader.readLine())!=null)
            {
                processLine(line);
            }
        }
        catch(Exception e)
        {
            e.printStackTrace();
        }
        finally
        {
            if(reader!=null)
                try{
                reader.close();
                }catch(Exception e){}

        }
    }

    private void processLine(String line) {
        String source=null,target=null;
        String[] parts=line.split(Pattern.quote("|||"));
        if (parts.length == 2)
        {
            target=parts[1].trim();
            String[] partsSrc=parts[0].split(Pattern.quote("--"));
            List<String> srcPartsL= new ArrayList<String>();
            for (String s: partsSrc)
                srcPartsL.add(s.trim());
            source=Util.join(srcPartsL, " ");

            ReplacementPattern rp=new ReplacementPattern(source, srcPartsL.size(),target);
            replacementPatterns.add(rp);
        }
    }    
}
