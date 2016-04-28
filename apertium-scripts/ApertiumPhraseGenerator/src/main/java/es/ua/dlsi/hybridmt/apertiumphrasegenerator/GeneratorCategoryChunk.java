/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import java.util.List;

/**
 *
 * @author vmsanchez
 */
public class GeneratorCategoryChunk {
    private String catName;
    private int size;
    private List<Chunk> lexicalForms;
    private int counter;
    private boolean endReached;

    public GeneratorCategoryChunk(String catName, List<Chunk> lexicalForms) {
        this.catName = catName;
        this.size = lexicalForms.size();
        this.lexicalForms = lexicalForms;
        this.counter = 0;
        this.endReached=false;
        if(counter>=size)
        {
            counter=0;
            endReached=true;
        }
    }

    public Chunk getCurrentWord()
    {
        return lexicalForms.get(counter);
    }

    public boolean increment()
    {
        if(counter==0)
            endReached=false;
        counter++;
        if(counter>=size)
        {
            counter=0;
            endReached=true;
        }
        return endReached;
    }

    public boolean isEndReached() {
        return endReached;
    }

    public void setEndReached(boolean endReached) {
        this.endReached = endReached;
    }

    

    public String getCatName() {
        return catName;
    }

    public void setCatName(String catName) {
        this.catName = catName;
    }


    public int getCounter() {
        return counter;
    }

    public void setCounter(int counter) {
        this.counter = counter;
         if(counter>=size)
        {
            counter=0;
            endReached=true;
        }
    }

    public List<Chunk> getLexicalForms() {
        return lexicalForms;
    }

    public void setLexicalForms(List<Chunk> lexicalForms) {
        this.lexicalForms = lexicalForms;
    }

    public int getSize() {
        return size;
    }

    public void setSize(int numberWords) {
        this.size = numberWords;
    }


}
