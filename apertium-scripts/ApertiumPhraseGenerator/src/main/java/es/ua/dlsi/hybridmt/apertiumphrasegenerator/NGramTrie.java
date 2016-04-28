/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import es.ua.dlsi.hybridmt.apertiumphrasegenerator.trie.Trie;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

/**
 *
 * @author vmsanchez
 */
public class NGramTrie {
    private Trie<String> trie;

    public NGramTrie() {
        trie = new Trie<String>("");
    }

    public boolean isNGram(List<String> ngram)
    {
       List<String> checkList= new ArrayList<String>();
       for (String s: ngram )
           checkList.add(Util.lowercaseApertiumWord(s));
       return trie.isElement(checkList);
    }

     public  boolean isInvalidNGram(List<String> accsource, int maxn) {
         NGramTrie filterTrie=this;
        for (int j = 0; j <= (accsource.size() - maxn); j++) {
            if (!filterTrie.isNGram(accsource.subList(j, j + maxn))) {
                return true;
            }
        }
        if (accsource.size() < maxn) {
            //for(int j=2; j<maxn; j++)
            //{
            if (!filterTrie.isNGram(accsource)) {
                return true;
            }
            //}
        }
        return false;
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

        String ngramsStr=null;
        if(line.matches("^\\dGRAM.*"))
        {
            ngramsStr=line.substring("GRAM".length()+1);
        }
        /*
        if (line.startsWith("BIGRAM"))
            ngramsStr=line.substring("BIGRAM".length());
        else if (line.startsWith("TRIGRAM"))
            ngramsStr=line.substring("TRIGRAM".length());
         *
         */
        if(ngramsStr!=null)
        {
            String[] ngramsArray= ngramsStr.split("---");
            
            List<String> ngramsList = new LinkedList<String>();
            boolean containsNullOrUnknown=false;
            for(String word: ngramsArray)
            {
                word=word.trim();
                if("NULL".equals(word) || word.startsWith("^*"))
                {
                    containsNullOrUnknown=true;
                    break;
                }
                ngramsList.add(Util.lowercaseApertiumWord(word));
            }
            if(!containsNullOrUnknown)
            {
                //debug
                /*
                for(String ng: ngramsList)
                {
                    System.err.print(ng);
                    System.err.print(" ");
                }
                System.err.println();
                */
                
                trie.insertElement(ngramsList);
            }
        }

    }
    
}
