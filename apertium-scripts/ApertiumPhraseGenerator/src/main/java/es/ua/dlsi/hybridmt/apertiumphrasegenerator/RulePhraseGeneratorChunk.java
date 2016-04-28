/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.ListIterator;

/**
 *
 * @author vmsanchez
 */
public class RulePhraseGeneratorChunk {

    private List<GeneratorCategoryChunk> categories;
    private boolean hasEmptyCategory;

    public RulePhraseGeneratorChunk(List<GeneratorCategoryChunk> categories) {
        this.categories = categories;

        for(GeneratorCategoryChunk cat: categories)
            if(cat.getSize()==0)
                hasEmptyCategory=true;
    }
    

    public List<GeneratorCategoryChunk> getCategories() {
        return categories;
    }

    public void setCategories(List<GeneratorCategoryChunk> categories) {
        this.categories = categories;
    }

    public boolean end()
    {
        return hasEmptyCategory || categories.get(0).isEndReached();
    }

    public List<Chunk> getCurrentPhrase()
    {
        List<Chunk> currentPhrase=new ArrayList<Chunk>();
        for (GeneratorCategoryChunk gc: categories)
        {
            currentPhrase.add(gc.getCurrentWord());
        }
        return currentPhrase;
    }

    public void step()
    {
       jump(categories.size()-1);
    }

    public void jump(int numWord)
    {
        for(int i=numWord+1; i<categories.size();i++)
        {
            categories.get(i).setCounter(0);
        }
        boolean limitReached=true;
        ListIterator<GeneratorCategoryChunk> iterator= categories.listIterator(numWord+1);
        while(iterator.hasPrevious() && limitReached)
        {
            GeneratorCategoryChunk category=iterator.previous();
            limitReached=category.increment();
        }
    }

    public int filterCurrentPhrase(NGramTrie filterTrie, int maxn) {
        
        List<Chunk> currentPhrase=getCurrentPhrase();
        int i=0;
        List<List<String>> accsources=new ArrayList<List<String>>();
        accsources.add(new ArrayList<String>());

        List<String> lastlist=accsources.get(accsources.size()-1);
        int completelyCheckedAcc=-1;
        
        int lastChunkFragmentId=-1;
        int lastChunkFragmentNumber=-1;
        boolean lastChunkFragmentFinished=true;

        boolean firstChunkOK=true;

        if(currentPhrase.size()>0)
        {
            if(currentPhrase.get(0) instanceof TrueChunk)
            {
                TrueChunk tc=(TrueChunk) currentPhrase.get(0);
                lastlist.addAll(tc.getSourceWords());
            }
            else
            {
                ChunkFragment cf = (ChunkFragment) currentPhrase.get(0);
                int id= cf.getId();
                int number=cf.getNumber();
                if(!lastChunkFragmentFinished)
                {
                    if(id!=lastChunkFragmentId)
                    {
                        firstChunkOK=false;
                    }
                }
                lastChunkFragmentId=id;
                if(number!=lastChunkFragmentNumber+1)
                {
                    firstChunkOK=false;
                }
                lastChunkFragmentNumber=number;
                if(cf.isIsLast())
                {
                    lastChunkFragmentFinished=true;
                    lastChunkFragmentId=-1;
                    lastChunkFragmentNumber=-1;
                }
            }
        }

        if(firstChunkOK)
        {
            for (i=1; i<currentPhrase.size();i++)
            {
                Chunk curChunk=currentPhrase.get(i);
                if(curChunk instanceof TrueChunk)
                {
                    TrueChunk tch=(TrueChunk) curChunk;
                    if(tch.getSourceWords().isEmpty())
                    {
                        System.err.println("WARNING: chunk with empty source: '"+tch.getSource()+"' | '"+curChunk.getChunk()+"'");
                    }
                    lastlist.addAll(tch.getSourceWords());

                    if(!lastChunkFragmentFinished)
                        break;

                    lastChunkFragmentFinished=true;
                    lastChunkFragmentId=-1;
                    lastChunkFragmentNumber=-1;
                }
                else
                {
                    accsources.add(new ArrayList<String>());
                    lastlist=accsources.get(accsources.size()-1);

                    ChunkFragment cf = (ChunkFragment) curChunk;
                    int id= cf.getId();
                    int number=cf.getNumber();
                    if(!lastChunkFragmentFinished)
                    {
                        if(id!=lastChunkFragmentId)
                        {
                            break;
                        }
                    }
                    lastChunkFragmentId=id;
                    if(number!=lastChunkFragmentNumber+1)
                    {
                        break;
                    }
                    lastChunkFragmentNumber=number;
                    if(cf.isIsLast())
                    {
                        lastChunkFragmentFinished=true;
                        lastChunkFragmentId=-1;
                        lastChunkFragmentNumber=-1;
                    }

                }

                boolean isInvalid=false;
                for(List<String> sourceseq: accsources.subList(0, completelyCheckedAcc+2))
                {
                    if(filterTrie.isInvalidNGram(sourceseq,maxn))
                    {
                        isInvalid=true;
                         break;
                    }
                }
                completelyCheckedAcc=accsources.size()-2;

                if (isInvalid)
                    break;
            }
            /*
            if(i<currentPhrase.size())
                return i+nlength-1;
            else
                return i;
             *
             */
            return i;
        }
        else
            return 0;
    }

   

}
