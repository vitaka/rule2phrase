/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import es.ua.dlsi.hybridmt.schemas.interchunk.CatItem;
import es.ua.dlsi.hybridmt.schemas.interchunk.DefCat;
import es.ua.dlsi.hybridmt.schemas.interchunk.Interchunk;
import es.ua.dlsi.hybridmt.schemas.interchunk.Pattern;
import es.ua.dlsi.hybridmt.schemas.interchunk.PatternItem;
import es.ua.dlsi.hybridmt.schemas.interchunk.Rule;
import java.io.IOException;
import java.io.Writer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;


/**
 *
 * @author vmsanchez
 */
public class ChunkPhraseGenerator {
    private static boolean DEBUG=true;
    
    private Interchunk interchunk;
    private ChunksTrie dictionary;
    private Map<String,ChunksTrie> catsTries;
    private Map<String,List<Chunk>> cachedCategories;
    private boolean debugTransfer;

    public ChunkPhraseGenerator(Interchunk transferRules,ChunksTrie dic, boolean dt) {
        interchunk=transferRules;
        catsTries=new HashMap<String, ChunksTrie>();
        dictionary=dic;
        cachedCategories= new HashMap<String, List<Chunk>>();
        debugTransfer=dt;
        createCategoryTries(interchunk,dictionary);
    }

    private void createCategoryTries(Interchunk interchunk, ChunksTrie dictionary) {
        for(DefCat defCat: interchunk.getSectionDefCats().getDefCat())
        {
            String catName=defCat.getN();
            ChunksTrie catTrie=new ChunksTrie(this.debugTransfer);
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
                ChunksTrie subtrie=dictionary.getSubtrie(taglist);

                if(catItem.getLemma()!=null)
                {
                    subtrie.pruneLemmas(catItem.getLemma());
                }

                catTrie.merge(subtrie);
            }
            catsTries.put(catName, catTrie);
        }
    }

    private List<Chunk> getLexicalFormsFromCat(String cat)
    {
        if(!cachedCategories.containsKey(cat))
            cachedCategories.put(cat, catsTries.get(cat).getChunkList());
        return cachedCategories.get(cat);
    }

    public  void generatePhrasesStrict(Writer output, NGramTrie filter, int ngramOrder)
    {
        System.err.println("Generating phrases");
        boolean generateTransferAls=this.debugTransfer;
        int numRules=interchunk.getSectionRules().getRule().size();
        int currentRule=0;
        for(Rule rule: interchunk.getSectionRules().getRule())
        {
            currentRule++;
            int numgeneratedLines=0;

            Pattern pattern=rule.getPattern();
            StringBuilder debugLine=new StringBuilder("Rule ");
            debugLine.append(currentRule).append(" of ").append(numRules).append(" : ");            

            boolean foundEmptyGeneratorCategory=false;
            List<GeneratorCategoryChunk> generatorCategorys=new ArrayList<GeneratorCategoryChunk>();
            for (PatternItem patternItem: pattern.getPatternItem())
            {
                String cat= ((DefCat)patternItem.getN()).getN();
                GeneratorCategoryChunk generatorCategory=new GeneratorCategoryChunk(cat,getLexicalFormsFromCat(cat));
                if(generatorCategory.getSize() == 0){
                    foundEmptyGeneratorCategory=true;
                    debugLine.append(cat).append(" (EMPTY) ");
                    break;
                }
                generatorCategorys.add(generatorCategory);

                debugLine.append(cat).append(" ");
            }
            if(foundEmptyGeneratorCategory){
                //Debug
                System.err.println(debugLine.toString());
                continue;
            }

            //Debug
            System.err.println(debugLine.toString());
            
            List<InterchunkMatchingHypothesis> hypotheses = new ArrayList<InterchunkMatchingHypothesis>();
            //Start with empty hypothesis
            hypotheses.add(new InterchunkMatchingHypothesis());
            
            for(GeneratorCategoryChunk generatorCategory: generatorCategorys){
                if(hypotheses.size() == 0){
                    break;
                }
                List<InterchunkMatchingHypothesis> newHypotheses = new ArrayList<InterchunkMatchingHypothesis>();
                for(Chunk chunk: generatorCategory.getLexicalForms()){
                    for(InterchunkMatchingHypothesis hyp: hypotheses){
                        if(hyp.canBeExtendedWithChunk(chunk,filter,dictionary)){
                            if(DEBUG){
                                System.err.println("Allowed");
                                System.err.println();
                            }
                            InterchunkMatchingHypothesis newHyp= hyp.extendWithChunk(chunk, dictionary);
                            newHypotheses.add(newHyp);
                        }else{
                            if(DEBUG){
                                System.err.println("Rejected");
                                System.err.println();
                            }
                        }
                    }
                }
                hypotheses=newHypotheses;
            }
            
            //TO DO: take care about alignment info in previous steps
            for(InterchunkMatchingHypothesis finalHyp: hypotheses){
                if(finalHyp.getSourceLexForms().size() > 0){
                    //Simply print final hypotheses
                    try{
                     if(generateTransferAls)
                        output.write(Util.join(finalHyp.getSourceLexForms() ," ") +" ||| "+Util.join(finalHyp.getChunks(), " ")+" ||| "+Util.join(finalHyp.getDebugInfos(), " ")+"\n");
                    else
                        output.write(Util.join(finalHyp.getSourceLexForms(), " ")+" ||| "+Util.join(finalHyp.getChunks(), " ")+"\n");
                     } catch (IOException ex) {
                         Logger.getLogger(ChunkPhraseGenerator.class.getName()).log(Level.SEVERE, null, ex);
                     }
                }
            }
                    
            
        }
    }
    
    public  void generatePhrases(Writer output, NGramTrie filter, int ngramOrder)
    {
        System.err.println("Generating phrases");
        boolean generateTransferAls=this.debugTransfer;
        int numRules=interchunk.getSectionRules().getRule().size();
        int currentRule=0;

        for(Rule rule: interchunk.getSectionRules().getRule())
        {
            currentRule++;
            int numgeneratedLines=0;

            Pattern pattern=rule.getPattern();
            StringBuilder debugLine=new StringBuilder("Rule ");
            debugLine.append(currentRule).append(" of ").append(numRules).append(" : ");            


            List<GeneratorCategoryChunk> generatorCategorys=new ArrayList<GeneratorCategoryChunk>();
            for (PatternItem patternItem: pattern.getPatternItem())
            {
                String cat= ((DefCat)patternItem.getN()).getN();
                GeneratorCategoryChunk generatorCategory=new GeneratorCategoryChunk(cat,getLexicalFormsFromCat(cat));
                generatorCategorys.add(generatorCategory);

                debugLine.append(cat).append(" ");
            }

            //Debug
            System.err.print(debugLine.toString());


            RulePhraseGeneratorChunk rulePhraseGenerator=new RulePhraseGeneratorChunk(generatorCategorys);
            while(!rulePhraseGenerator.end())
            {
                int firstNotAllowedWord=rulePhraseGenerator.filterCurrentPhrase(filter,ngramOrder);
                if(firstNotAllowedWord>=generatorCategorys.size())
                {
                    int lastmultiid=-1;
                    
                    List<Chunk> words=rulePhraseGenerator.getCurrentPhrase();

                    List<List<TrueChunk>> wordsToPrint=new LinkedList<List<TrueChunk>>();
                    wordsToPrint.add(new ArrayList<TrueChunk>());

                    List<ChunkFragment> multiList=new LinkedList<ChunkFragment>();

                    boolean correctOutput=true;

                    boolean prevUnit=true;
                    int prevNumber=-1;

                    Iterator<Chunk> it=words.iterator();
                    while(it.hasNext() && wordsToPrint.size()>0)
                    {
                        Chunk ch=it.next();
                        if( ch instanceof ChunkFragment)
                        {
                            ChunkFragment chf=(ChunkFragment) ch;

                            int id=chf.getId();
                            int number=chf.getNumber();
                            boolean end=chf.isIsLast();

                            multiList.add(chf);

                            if(number!=prevNumber+1)
                            {
                                correctOutput=false;
                                break;
                            }
                            else
                            {
                                if(number>0 )
                                {
                                    if(id!=lastmultiid)
                                    {
                                        correctOutput=false;
                                        break;
                                    }
                                }

                                if(end)
                                {

                                    List<Pair<String>> sources=dictionary.getMultiChunkSources(multiList);
                                    List<List<TrueChunk>> newWordsToPrint=new LinkedList<List<TrueChunk>>();

                                    for(List<TrueChunk> l: wordsToPrint)
                                    {
                                        for(Pair<String> s: sources)
                                        {
                                            List<TrueChunk> seq= new ArrayList<TrueChunk>();
                                            seq.addAll(l);
                                            seq.add(new TrueChunk(Util.joinChunksf(multiList, " ") , s.getFirst(), s.getSecond()));
                                            
                                            List<String> lsources=new ArrayList<String>();
                                            for(TrueChunk tc: seq)
                                                lsources.addAll(tc.getSourceWords());
                                            if(!filter.isInvalidNGram(lsources, ngramOrder ));
                                                newWordsToPrint.add(seq);
                                        }
                                    }

                                    wordsToPrint.clear();
                                    wordsToPrint.addAll(newWordsToPrint);

                                    prevNumber=-1;
                                    prevUnit=true;
                                    multiList.clear();
                                }
                                else
                                {
                                    lastmultiid=id;
                                    prevNumber=number;
                                    prevUnit=false;
                                }
                            }
                        }
                        else
                        {
                            if(prevUnit==false)
                            {
                                correctOutput=false;
                                break;
                            }
                            prevUnit=true;
                            for(List<TrueChunk> l: wordsToPrint)
                            {
                                l.add((TrueChunk) ch);
                            }
                        }
                    }

                    if(correctOutput && prevUnit)
                    {
                        for(List<TrueChunk> listToPrint: wordsToPrint)
                        {
                            try {
                                if(generateTransferAls)
                                    output.write(Util.joinSources(listToPrint, " ")+" ||| "+Util.joinChunks(listToPrint, " ")+" ||| "+Util.joinTransferDebug(listToPrint, " ")+"\n");
                                else
                                    output.write(Util.joinSources(listToPrint, " ")+" ||| "+Util.joinChunks(listToPrint, " ")+"\n");
                                
                                numgeneratedLines++;
                            } catch (IOException ex) {
                                Logger.getLogger(ChunkPhraseGenerator.class.getName()).log(Level.SEVERE, null, ex);
                            }
                        }
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
