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
public class RulePhraseGenerator {

    private List<GeneratorCategory> categories;
    boolean hasEmptyCategory=false;

    public RulePhraseGenerator(List<GeneratorCategory> categories) {
        this.categories = categories;
        for(GeneratorCategory category: this.categories)
        {
            if(category.getSize()==0)
                hasEmptyCategory=true;
        }
    }
    

    public List<GeneratorCategory> getCategories() {
        return categories;
    }

    public void setCategories(List<GeneratorCategory> categories) {
        this.categories = categories;
    }

    public boolean end()
    {
        return hasEmptyCategory || categories.get(0).isEndReached();
    }

    public List<String> getCurrentPhrase()
    {
        List<String> currentPhrase=new ArrayList<String>();
        for (GeneratorCategory gc: categories)
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
        ListIterator<GeneratorCategory> iterator= categories.listIterator(numWord+1);
        while(iterator.hasPrevious() && limitReached)
        {
            GeneratorCategory category=iterator.previous();
            limitReached=category.increment();
        }
    }

    public int filterCurrentPhrase(NGramTrie filterTrie, int maxn) {
        List<String> currentPhrase=getCurrentPhrase();
        int i=0;
        int nlength=0;
        for (i=0; i<currentPhrase.size();i++)
        {
            List<String> ngram=new ArrayList<String>();
            for(int j=0; j<maxn && j+i<currentPhrase.size(); j++)
            {
                ngram.add(currentPhrase.get(i+j));
            }

            boolean isInvalid=false;
            for(int k=1 ; k<= ngram.size();k++)
            {
                nlength=k;
                if(!filterTrie.isNGram(ngram.subList(0, k)))
                {
                    isInvalid=true;
                    break;
                }
            }
            if (isInvalid)
            {
                break;
            }
        }
        if(i<currentPhrase.size())
            return i+nlength-1;
        else
            return i;
    }

   


}
