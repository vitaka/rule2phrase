/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 *
 * @author vmsanchez
 */
public class InterchunkMatchingHypothesis {
    private static boolean DEBUG=true;
    
    private List<Chunk> chunkObjects;
    private List<String> chunks;
    private List<String> sourceLexForms;
    private List<String> debugInfos;

    public InterchunkMatchingHypothesis() {
        chunks= new ArrayList<String>();
        sourceLexForms= new ArrayList<String>();
        debugInfos= new ArrayList<String>();
        chunkObjects = new ArrayList<Chunk>();
    }
    
    
    public boolean canBeExtendedWithChunk(Chunk c, NGramTrie ntrie, ChunksTrie dictionary){
        if(DEBUG){
            System.err.println("Trying to add new chunk to hypothesis:");
            System.err.println("Current hypothesis chunks: "+Util.join(chunks, "#"));
            System.err.println("Current hypotheiss source lex forms: "+Util.join(sourceLexForms, "#"));
            
            System.err.println("Chunk being evaluated: "+c.getChunk());
        }
        
        
        
        if(c instanceof TrueChunk){
            TrueChunk tc = (TrueChunk) c;
            
            //check whether the last chunk is an unfinished fragment. 
            // If it is, we cannot add a true chunk
            if(chunkObjects.size() > 0){
                if(chunkObjects.get(chunkObjects.size()-1) instanceof ChunkFragment){
                   ChunkFragment cfragment = (ChunkFragment) chunkObjects.get(chunkObjects.size()-1);
                   if(!cfragment.isIsLast()){
                       return false;
                   }
                }
            }
            
            //Check lexical form ngrams
            List<String> newLexFormSeq= new ArrayList<String>(sourceLexForms);
            newLexFormSeq.addAll(tc.getSourceWords());
            if(ntrie.isNGram(newLexFormSeq)){
                return true;
            }else{
                return false;
            }
        }else{
            //c is ChunkFragment instance
            ChunkFragment cf = (ChunkFragment) c;
            
            //If it is not the first one, it should match
            if(cf.getNumber() > 0){
                if(chunkObjects.size() == 0){
                    return false;
                }
                if( !(chunkObjects.get(chunkObjects.size()-1) instanceof ChunkFragment)){
                    return false;
                }
                if( ((ChunkFragment)chunkObjects.get(chunkObjects.size()-1)).getNumber() != cf.getNumber()-1  ){
                    return false;
                }
                if( ((ChunkFragment)chunkObjects.get(chunkObjects.size()-1)).getId() != cf.getId()  ){
                    return false;
                }
            }
            
            //If it is the last one, sequence of lexical forms must be found in allowed ngram list
            if(cf.isIsLast()){
                List<Pair<String>> lexicalFormsFromMultichunk = getMultiChunkSource(cf, dictionary);
                if(lexicalFormsFromMultichunk.size() == 0){
                    return false;
                }
                
                List<String> sourceWordsFromMultichunk= new ArrayList<String>();
                for(Pair<String> lexpair: lexicalFormsFromMultichunk){
                    sourceWordsFromMultichunk.add(lexpair.getFirst());
                }
                
                //Check lexical form ngrams
                List<String> newLexFormSeq= new ArrayList<String>(sourceLexForms);
                newLexFormSeq.addAll(sourceWordsFromMultichunk);
                List<String> fixedNewLexFormSeq = splitLexicalFormsFromMultichunk(newLexFormSeq);
                if(ntrie.isNGram(fixedNewLexFormSeq)){
                    return true;
                }else{
                    return false;
                }
            }else{
                return true;
            }
                  
            
        }
    }

    private List<Pair<String>> getMultiChunkSource(ChunkFragment cf, ChunksTrie dictionary) {
        //Get full list of chunk fragments
        List<ChunkFragment> reversedChunkFragmentList = new ArrayList<ChunkFragment>();
        reversedChunkFragmentList.add(cf);
        for(int i=chunkObjects.size()-1; i>=0 && (chunkObjects.get(i) instanceof ChunkFragment) && ((ChunkFragment) chunkObjects.get(i)).getId() == cf.getId() ; i--){
            reversedChunkFragmentList.add((ChunkFragment) chunkObjects.get(i));
        }
        //Variable name is wrong: after this operation, they are not reversed
        Collections.reverse(reversedChunkFragmentList);
        List<Pair<String>> lexicalFormsFromMultichunk= dictionary.getMultiChunkSources(reversedChunkFragmentList);
        
        
        //Only for debug purposes
        if(DEBUG){
        List<String> strChunks = new ArrayList<String>();
        for(Chunk chunk: reversedChunkFragmentList){
            strChunks.add(chunk.getChunk());
        }
        System.err.println("Result of building multichunk: "+Util.join(strChunks," "));
        List<String> lexforms= new ArrayList<String>();
        List<String> debugInfos= new ArrayList<String>();
        for(Pair<String> p: lexicalFormsFromMultichunk){
            lexforms.add(p.getFirst());
            debugInfos.add(p.getSecond());
        }
        System.err.println("Lexforms: "+Util.join(lexforms, "#"));
        System.err.println("Lexforms after fix them: "+Util.join(splitLexicalFormsFromMultichunk(lexforms), "#"));
        System.err.println("ChunkDebug: "+Util.join(debugInfos, "#"));
        }
        
        
        return lexicalFormsFromMultichunk;
    }
    
    public static List<String> splitLexicalFormsFromMultichunk(List<String> input){
        List<String> output = new ArrayList<String>();
        for(String str: input){
            String[] splitparts= str.split("\\$ \\^",-1);
            int numParts=splitparts.length;
            for(int i=0; i< splitparts.length; i++){
                String mypart=splitparts[i];
                if(numParts > 1){
                    if(i > 0){
                        mypart="^"+mypart;
                    }
                    if(i < numParts -1){
                        mypart=mypart+"$";
                    }
                }
                output.add(mypart);
                       
            }
        }
        return output;
    }
    
    InterchunkMatchingHypothesis extendWithChunk(Chunk c, ChunksTrie dictionary){
        
        InterchunkMatchingHypothesis newHyp = new InterchunkMatchingHypothesis();
        newHyp.chunks.addAll(this.chunks);
        newHyp.sourceLexForms.addAll(this.sourceLexForms);
        newHyp.debugInfos.addAll(this.debugInfos);
        newHyp.chunkObjects.addAll(this.chunkObjects);
        
        newHyp.chunkObjects.add(c);
        newHyp.chunks.add(c.getChunk());
        
        if(c instanceof TrueChunk){
            TrueChunk tc = (TrueChunk) c;
            newHyp.sourceLexForms.addAll(tc.getSourceWords());
            newHyp.debugInfos.add(tc.getDebugTransfer());
            
        }
        else{
            //ChunkFragment
            ChunkFragment cf=(ChunkFragment) c;
            
            if(cf.isIsLast()){
            //If this fragment is the last, add lexical forms and debug info from MultiChunkTrie
            List<Pair<String>> lexicalFormsFromMultichunk = getMultiChunkSource(cf, dictionary);
            List<String> sourceLexicalForms= new ArrayList<String>();
            List<String> debugInfosToAdd= new ArrayList<String>();
            for(Pair<String> p: lexicalFormsFromMultichunk){
                sourceLexicalForms.add(p.getFirst());
                debugInfosToAdd.add(p.getSecond());
            }
            
            newHyp.sourceLexForms.addAll(splitLexicalFormsFromMultichunk(sourceLexicalForms) );
            newHyp.debugInfos.addAll(debugInfosToAdd);
            }
            
        }
        
        
        return newHyp;
    }

    public List<String> getChunks() {
        return chunks;
    }

    public List<String> getSourceLexForms() {
        return sourceLexForms;
    }

    public List<String> getDebugInfos() {
        return debugInfos;
    }
    
    
}
