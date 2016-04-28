/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import es.ua.dlsi.hybridmt.schemas.transfer.CatItem;
import es.ua.dlsi.hybridmt.schemas.transfer.DefCat;
import es.ua.dlsi.hybridmt.schemas.transfer.Pattern;
import es.ua.dlsi.hybridmt.schemas.transfer.PatternItem;
import es.ua.dlsi.hybridmt.schemas.transfer.Rule;
import java.io.IOException;
import java.io.Writer;
import es.ua.dlsi.hybridmt.schemas.transfer.Transfer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;


/**
 *
 * @author vmsanchez
 */
public class PhraseGenerator {

    private Transfer transfer;
    private WordsTrie dictionary;
    private Map<String,WordsTrie> catsTries;
    private Map<String,List<String>> cachedCategories;

    public PhraseGenerator(Transfer transferRules, WordsTrie dic) {
        transfer=transferRules;
        catsTries=new HashMap<String, WordsTrie>();
        dictionary=dic;
        cachedCategories= new HashMap<String, List<String>>();
        createCategoryTries(transfer,dictionary);
    }
    
    public Map<String,WordsTrie> getCategoriesTries(){
        return this.catsTries;
    }
    
    private void createCategoryTries(Transfer transfer, WordsTrie dictionary) {
        for(DefCat defCat: transfer.getSectionDefCats().getDefCat())
        {
            String catName=defCat.getN();
            WordsTrie catTrie=new WordsTrie();
            for(CatItem catItem: defCat.getCatItem())
            {
                String tags=catItem.getTags();
                String[] tagsArray=tags.split("\\.");
                List<String> taglist=new LinkedList<String>();
                for(String s: tagsArray)
                {
                    if("*".equals(s.trim()))
                        taglist.add("*");
                    else
                        taglist.add("<"+s.trim()+">");
                }

                //ATENCION: para n.*, el subtrie solo tiene dos nodos: root y n
                //get subtrie
                WordsTrie subtrie=dictionary.getSubtrie(taglist);
                
                if(catItem.getLemma()!=null)
                {
                    subtrie.pruneLeaves(catItem.getLemma());
                }
                
                catTrie.merge(subtrie);
            }
            catsTries.put(catName, catTrie);
        }
    }

    private List<String> getLexicalFormsFromCat(String cat)
    {
        if(!cachedCategories.containsKey(cat))
            cachedCategories.put(cat, catsTries.get(cat).getWordList());
        return cachedCategories.get(cat);
    }

    public  void generatePhrases(Writer output, NGramTrie filter, int ngramOrder)
    {   
        int numRules=transfer.getSectionRules().getRule().size();
        int currentRule=0;

        for(Rule rule: transfer.getSectionRules().getRule())
        {
            currentRule++;
            int numgeneratedLines=0;

            Pattern pattern=rule.getPattern();

            StringBuilder debugLine=new StringBuilder("Rule ");
            debugLine.append(currentRule).append(" of ").append(numRules).append(" : ");


            List<GeneratorCategory> generatorCategorys=new ArrayList<GeneratorCategory>();
            for (PatternItem patternItem: pattern.getPatternItem())
            {
                String cat= ((DefCat)patternItem.getN()).getN();
                GeneratorCategory generatorCategory=new GeneratorCategory(cat,getLexicalFormsFromCat(cat));
                generatorCategorys.add(generatorCategory);

                debugLine.append(cat).append(" ");
            }

            //Debug
            System.err.println(debugLine.toString());

           
            RulePhraseGenerator rulePhraseGenerator=new RulePhraseGenerator(generatorCategorys);
            while(!rulePhraseGenerator.end())
            {
                int firstNotAllowedWord=rulePhraseGenerator.filterCurrentPhrase(filter,ngramOrder);
                if(firstNotAllowedWord>=generatorCategorys.size())
                {
                    List<String> words=rulePhraseGenerator.getCurrentPhrase();
                    
                    //Debug
                    //System.err.println("OK: "+Util.join(words, " "));

                    try {
                        output.write(Util.join(words, " ")+"\n");
                        numgeneratedLines++;
                    } catch (IOException ex) {
                        Logger.getLogger(PhraseGenerator.class.getName()).log(Level.SEVERE, null, ex);
                    }
                    rulePhraseGenerator.step();
                }
                else
                {
                    //Debug
                     //List<String> words=rulePhraseGenerator.getCurrentPhrase();
                    //System.err.println("Not in trie: "+Util.join(words, " ")+". First not valid position: "+Integer.toString(firstNotAllowedWord));
                    rulePhraseGenerator.jump(firstNotAllowedWord);
                }
            }
            
            
            System.err.println(" - "+Integer.toString(numgeneratedLines)+" generated lines");
            /*
            for(String cat: categories)
            {
                System.out.print(cat+"("+Integer.toString(getLexicalFormsFromCat(cat).size())+") ");
            }
            System.out.println();
             * 
             */
        }
    }
}
