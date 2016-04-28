/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import es.ua.dlsi.hybridmt.apertiumphrasegenerator.trie.Node;
import es.ua.dlsi.hybridmt.apertiumphrasegenerator.trie.Trie;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *
 * @author vmsanchez
 */
public class WordsTrie {

    private Trie<String> trie;
    private static Pattern tagPattern=Pattern.compile("<([^>]+)>");

    public WordsTrie() {
        trie= new Trie<String>("");
    }
    
    public boolean containsElement(List<String> myElement){
        return trie.isElement(myElement);
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

    public List<String> getWordList()
    {
        List<String> wordList=new ArrayList<String>();

        List<List<String>> trieList= trie.getItemList();
        for (List<String> item: trieList)
        {
            if(item.size()>1)
            {
                String lemma=item.remove(item.size()-1);
                item.add(0, lemma);
                wordList.add("^"+Util.join(item, "")+"$");
            }
        }

        return wordList;
    }

    public WordsTrie getSubtrie(List<String> taglist) {
        WordsTrie subwtrie=new WordsTrie();

        boolean strict=true;
        if("*".equals(taglist.get(taglist.size()-1)))
        {
            strict=false;
            taglist=taglist.subList(0, taglist.size()-1);
        }

        Trie<String> subTrie=trie.getSubTrie(taglist, "");
        if (strict && subTrie!=null)
        {
            Node<String> node=subTrie.getNode(taglist);
            Set<String> toRemove= new HashSet<String>();
            for(String key: node.getChildren().keySet())
            {
                if(key.startsWith("<"))
                {
                    toRemove.add(key);
                }
            }
            for(String key:toRemove)
            {
                node.getChildren().remove(key);
            }
        }

        if (subTrie!=null)
            subwtrie.trie=subTrie;
        return subwtrie;
    }

    public void merge(WordsTrie wt)
    {
        this.trie.merge(wt.trie);
    }

    private void processLine(String line)
    {
        List<String> tags = getTrieListFromLexicalForm(line);
        if (tags != null){
            trie.insertElement(tags);
        }
    }
 
    public void pruneLeaves(String lemma) {
        Set<String> allowedLemmas= new HashSet<String>();
        allowedLemmas.add(lemma);
        trie.pruneLeaves(allowedLemmas);
    }
    
     public static List<String> getTrieListFromLexicalForm(String lexicalForm){
         return getTrieListFromLexicalForm(lexicalForm, false);
     }
    
    public static List<String> getTrieListFromLexicalForm(String lexicalForm, boolean lowercase){
        String lemma;
        List<String> tags=new LinkedList<String>();
        
        int startTags=lexicalForm.indexOf("<");
        if (startTags >-1)
        {
            if(lowercase)
                lexicalForm=Util.lowercaseApertiumWord(lexicalForm);
            
            lemma=lexicalForm.substring(1, startTags);
            Matcher m=tagPattern.matcher(lexicalForm.substring(startTags));
            while(m.find())
            {
                tags.add(m.group());
            }
            tags.add(lemma);
            return tags;
        }
        return null;
    }
            
            
    

}
