/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import es.ua.dlsi.hybridmt.apertiumphrasegenerator.trie.Trie;
import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author vitaka
 */
public class MultiChunkTrie {

     private Trie<String> trie;

    public MultiChunkTrie() {
        trie = new Trie<String>("");
    }


    public void addMultiChunk(List<String> chunks, String source)
    {
        List<String> in= new ArrayList<String>();
        in.addAll(chunks);
        in.add(source);
        trie.insertElement(in);
    }

    public List<String> getSources(List<String> chunks)
    {
        List<String> sources=new ArrayList<String>();

        Trie<String> subtrie=trie.getSubTrie(chunks, "");
        if(subtrie!=null)
        {
            List<List<String>> l= subtrie.getItemList();

            for(List<String> c: l)
            {
                if(c.size()==chunks.size()+2)
                {
                    String source=c.get(c.size()-1);
                    sources.add(source);
                }
            }
        }
        else
            System.err.println("ERROR: MUltichunk not found '"+Util.join(chunks, " ")+"'");
        return sources;
    }

    public List<List<String>> getMultiChunks()
    {
        return trie.getItemList();
    }
     
}
