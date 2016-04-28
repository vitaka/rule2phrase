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
public class ChunksTrie {

    private Trie<String> trie;
    //private List<MultiChunk> multiChunkList;
    private MultiChunkTrie multiChunkTrie;
    private Pattern tagPattern=Pattern.compile("<([^>]+)>");
    private boolean debugTransfer=false;

   private int idmultichunk=0;

    //Debug
    private int maxmultichunk=0;

    
    public ChunksTrie() {
        trie= new Trie<String>("");
        //multiChunkList=new LinkedList<MultiChunk>();
        multiChunkTrie=new MultiChunkTrie();
    }


    public ChunksTrie(boolean debugTransfer) {
        trie= new Trie<String>("");
        //multiChunkList=new LinkedList<MultiChunk>();
        multiChunkTrie=new MultiChunkTrie();
        this.debugTransfer=debugTransfer;
    }

    public ChunksTrie filterGivenSources(NGramTrie ngrams)
    {
        ChunksTrie copy = new ChunksTrie(this.debugTransfer);
        List<List<String>> trieList= trie.getItemList();
        for (List<String> item: trieList)
        {
            if(item.size()>2)
            {
                item.remove(0);
                String source=item.get(item.size()-1);
                if (source.startsWith("^"))
                {
                    String sourceToSplit=source;
                    if(debugTransfer)
                    {
                         int pos= source.indexOf(" ||| ");
                         sourceToSplit=source.substring(0,pos).trim();
                    }
                    List<String> sourceList=TrueChunk.parseSourceWords(sourceToSplit);
                    if(!ngrams.isInvalidNGram(sourceList, 3))
                    {
                        copy.trie.insertElement(item);
                    }
                }
            }
        }

        int idmultichunk=0;
        for(List<String> multichunk: this.multiChunkTrie.getMultiChunks())
        {
            if(multichunk.size()>2)
            {
                multichunk.remove(0);
                String source=multichunk.remove(multichunk.size()-1);
                String sourceToSplit=source;
                if(debugTransfer)
                {
                     int pos= source.indexOf(" ||| ");
                     sourceToSplit=source.substring(0,pos).trim();
                }
                List<String> sourceList=TrueChunk.parseSourceWords(sourceToSplit);
                if(!ngrams.isInvalidNGram(sourceList, 3))
                {

                    for(int i=0; i<multichunk.size();i++)
                    {
                    
                        String chunkStr=multichunk.get(i);

                        int startChunk=chunkStr.indexOf("^");
                        List<String> tags= new LinkedList<String>();
                        int startTags=chunkStr.indexOf("<", startChunk);
                        int startWords=chunkStr.indexOf("{",startChunk);

                        if(startTags <0 || startTags > startWords)
                            startTags=startWords;

                        //debug
                        //System.err.println(chunkStr);

                        String lemma=chunkStr.substring(startChunk+1, startTags).trim().toLowerCase();

                        int endWords=chunkStr.indexOf("}$",startWords);
                        if(startTags< startWords)
                        {
                            Matcher m=tagPattern.matcher(chunkStr.substring(startTags,startWords));
                            while(m.find())
                            {
                                tags.add(m.group());
                            }
                        }
                        tags.add(lemma);
                        tags.add(chunkStr.substring(startWords+1, endWords));

                        String lastPiece="a";
                        if(i==multichunk.size()-1)
                            lastPiece="$";
                        
                        tags.add("_mchunk_"+idmultichunk+"]"+Integer.toString(i)+"_"+lastPiece+"_");
                        copy.trie.insertElement(tags);

                    }
                    
                    idmultichunk++;
                    copy.multiChunkTrie.addMultiChunk(multichunk, source);

                }
            }
        }

        return copy;

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

        //debug
        //System.err.println("Max multichunk length: "+maxmultichunk);
    }

    public List<Pair<String>> getMultiChunkSources(List<ChunkFragment> chunks)
    {
        List<Pair<String>> value= new ArrayList<Pair<String>>();
        List<String> strChunks=new ArrayList<String>();
        for(Chunk c: chunks)
        {
            strChunks.add(c.getChunk());
        }
        
       List<String> strSources= multiChunkTrie.getSources(strChunks);
       for (String strs: strSources)
           value.add(Util.splitSourceAndTransfer(strs));

       return value;
    }

    public List<Chunk> getChunkList()
    {
        List<Chunk> wordList=new ArrayList<Chunk>();

        List<List<String>> trieList= trie.getItemList();
        for (List<String> item: trieList)
        {
            if(item.size()>2)
            {
                item.remove(0);
                String source=item.remove(item.size()-1);
                if (source.startsWith("^"))
                {
                    String words=item.remove(item.size()-1);
                    String lemma=item.remove(item.size()-1);
                    item.add(0, lemma);
                    if(debugTransfer)
                    {
                        int pos= source.indexOf(" ||| ");
                        wordList.add(new TrueChunk("^"+Util.join(item, "")+"{"+words+"}"+"$", source.substring(0,pos).trim(), source.substring(pos+" ||| ".length()).trim())  );
                    }
                    else
                    {
                        wordList.add(new TrueChunk("^"+Util.join(item, "")+"{"+words+"}"+"$", source)  );
                    }
                }
                else if(source.startsWith("_mchunk_"))
                {
                    String words=item.remove(item.size()-1);
                    String lemma=item.remove(item.size()-1);
                    item.add(0, lemma);

                    int id=Integer.parseInt(source.substring(8, source.indexOf("]",8)));
                    int number=Integer.parseInt(source.substring(source.indexOf("]",8)+1, source.indexOf("_",8)));
                    boolean end=false;
                    if(source.charAt(source.indexOf("_",8)+1)=='$')
                         end=true;

                    wordList.add(new ChunkFragment("^"+Util.join(item, "")+"{"+words+"}"+"$", id,number,end)  );
                }
            }
        }

        return wordList;
    }

    public ChunksTrie getSubtrie(List<String> taglist) {
        ChunksTrie subwtrie=new ChunksTrie(this.debugTransfer);

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

    public void merge(ChunksTrie wt)
    {
        this.trie.merge(wt.trie);
    }

    private void processLine(String line)
    {
        boolean hasDebugInfo=this.debugTransfer;
        String lemma;
        String debugTransfer=null;
       

        List<List<String>> chunks=new LinkedList<List<String>>();
        List<String> chunksStr=new LinkedList<String>();

        //System.err.println("Processing line '"+line+"'");

        String[] parts= line.split(Pattern.quote(" ||| "));
        String source=parts[0].trim();
         line=parts[1].trim();
        if(hasDebugInfo)
        {
            debugTransfer=parts[2].trim();
        }
        
           


        /*
        int posSep=line.indexOf(" ||| ");
        String source=line.substring(0, posSep);
        line=line.substring(posSep+" ||| ".length());

        if(hasDebugInfo)
        {
             posSep=line.indexOf(" ||| ");
             debugTransfer=line.substring(posSep+" ||| ".length());
             line=line.substring(0,posSep);
        }*/

        int startChunk=line.indexOf("^");
        while (startChunk >-1)
        {
            List<String> tags= new LinkedList<String>();

            int startTags=line.indexOf("<", startChunk);
            int startWords=line.indexOf("{",startChunk);
            
            if(startTags <0 || startTags > startWords)
                startTags=startWords;

            lemma=line.substring(startChunk+1, startTags).trim().toLowerCase();

            int endWords=line.indexOf("}$",startWords);

            if(startTags< startWords)
            {
                Matcher m=tagPattern.matcher(line.substring(startTags,startWords));
                while(m.find())
                {
                    tags.add(m.group());
                }
            }
            tags.add(lemma);
            tags.add(line.substring(startWords+1, endWords));

            chunks.add(tags);
            //chunksStr.add(line.substring(startChunk,endWords+2));
            chunksStr.add("^"+lemma+line.substring(startTags, endWords+2));
            startChunk=line.indexOf("^",endWords);
        }

        
        String srcToAdd=source;
        if(debugTransfer!=null)
            srcToAdd=srcToAdd+" ||| "+debugTransfer.trim();

        if(chunks.size()==1)
        {
            List<String> chunk=chunks.get(0);
            chunk.add(srcToAdd);
            trie.insertElement(chunk);
        }
        else if (chunks.size()>1)
        {
            //MultiChunk mc=new MultiChunk(chunks, source);
            //multiChunkList.add(mc);

            for(int i=0; i<chunks.size();i++)
            {
                List<String> chunk=chunks.get(i);
                String lastPiece="a";
                if(i==chunks.size()-1)
                    lastPiece="$";
                chunk.add("_mchunk_"+idmultichunk+"]"+Integer.toString(i)+"_"+lastPiece+"_");
                trie.insertElement(chunk);
            }

            multiChunkTrie.addMultiChunk(chunksStr, srcToAdd);

            idmultichunk++;

            //debug
            if(chunks.size()>maxmultichunk)
                maxmultichunk=chunks.size();
        }
    }

    public void pruneLemmas(String lemma) {
        Set<String> allowedLemmas= new HashSet<String>();
        allowedLemmas.add(lemma);
        trie.pruneLeaves(allowedLemmas,2);
    }

}
