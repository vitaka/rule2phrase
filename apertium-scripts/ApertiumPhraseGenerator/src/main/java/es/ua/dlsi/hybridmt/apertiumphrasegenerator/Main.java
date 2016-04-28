package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import es.ua.dlsi.hybridmt.schemas.interchunk.Interchunk;
import es.ua.dlsi.hybridmt.schemas.transfer.DefCat;
import es.ua.dlsi.hybridmt.schemas.transfer.Pattern;
import es.ua.dlsi.hybridmt.schemas.transfer.PatternItem;
import es.ua.dlsi.hybridmt.schemas.transfer.Rule;
import es.ua.dlsi.hybridmt.schemas.transfer.Transfer;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import javax.xml.bind.JAXBContext;
import javax.xml.bind.Unmarshaller;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.PosixParser;

/**
 * Hello world!
 *
 */
public class Main
{
    public static void main( String[] args ) throws Exception
    {

        String lexformsFile=null;
        String rulesFile=null;
        String ngramsFile=null;
        int numNGramsFiles=-1;

        int ngramOrder=3;

        String splitFile=null;

        boolean generateAlignments=true;

        //Parse command line
        Options options = new Options();

        options.addOption("g", "generate",false,"Generate lexical forms");
        options.addOption("p","pretransfer_reverse",false,"Reverse pretransfer by joining lexical forms");
        options.addOption("x", "generate2level" ,  false, "Generate lexical forms using 2nd level of transfer");

        options.addOption("l", "lexforms", true, "Lexical forms file");
        options.addOption("r", "rules", true, "Apertium transfer rules file");
        options.addOption("t", "trie", true, "Ngrams file");
        options.addOption("m", "multipleNgrams",true,"Number of ngrams files");

        options.addOption("s","split_words",true,"Split words file");
        options.addOption("n","no_alignments",false,"Do not generate alignments (faster)");

        options.addOption("o","ngramOrder",true,"N-gram order");

        CommandLineParser clparser = new PosixParser();
        CommandLine line = clparser.parse( options, args );

        if(line.hasOption("g") || line.hasOption("x"))
        {

        if (line.hasOption("l"))
            lexformsFile=line.getOptionValue("l");
        if (line.hasOption("r"))
            rulesFile=line.getOptionValue("r");
        if(line.hasOption("t"))
            ngramsFile=line.getOptionValue("t");
        if(line.hasOption("m"))
            numNGramsFiles=Integer.parseInt(line.getOptionValue("m"));
        if(line.hasOption("o"))
            ngramOrder=Integer.parseInt(line.getOptionValue("o"));

        }
        else if(line.hasOption("p"))
        {
            if(line.hasOption("s"))
                splitFile=line.getOptionValue("s");
        }
        if(line.hasOption("n"))
                generateAlignments=false;

        if ( ( !line.hasOption("p") && !line.hasOption("g") && !line.hasOption("x")) || (line.hasOption("p")  && splitFile==null)  || (line.hasOption("g") && (lexformsFile==null || rulesFile==null || ngramsFile==null)) || (line.hasOption("x") && (lexformsFile==null || rulesFile==null  || ngramsFile==null ))  )
        {
            System.err.println("wrong parameters");
            HelpFormatter formatter = new HelpFormatter();
            formatter.printHelp( "ApertiumPhraseGenerator", options );
            System.exit(1);
        }

        if(line.hasOption("g"))
        {
            boolean DEBUG=false;
            
            //Loading rules
            File f = new File(rulesFile);
            JAXBContext context = JAXBContext.newInstance(Transfer.class);
            Unmarshaller u = context.createUnmarshaller();
            Transfer transfer = (Transfer) u.unmarshal(f);

            //Load lexical forms
            WordsTrie wordsTrie=new WordsTrie();
            wordsTrie.loadFromFile(new File(lexformsFile));

            //Load bigrams and trigrams
            //NGramTrie nGramTrie=new NGramTrie();
            //nGramTrie.loadFromFile(new File(ngramsFile));
                        
            //New method for generating rules:
            //for each NGram, check all the rules of the same lengthm and whether all words match
            
            //Only the category tries component of phrase generator is used
            PhraseGenerator phraseGenerator=new PhraseGenerator(transfer,wordsTrie);
            
            //Rules are just lists of category names, grouped by length
            Map<Integer,List<List<String>>> groupedRules = new HashMap<Integer,List<List<String>>>();
            //Iterate over pattern section
            for(Rule rule: transfer.getSectionRules().getRule())
            {
                Pattern pattern=rule.getPattern();
                List<String> categorySeq= new ArrayList<String>();
                for (PatternItem patternItem: pattern.getPatternItem())
                {
                    String cat= ((DefCat)patternItem.getN()).getN();
                    categorySeq.add(cat);
                }
                int length = categorySeq.size();
                if (length > 0){
                    if(!groupedRules.containsKey(length)){
                        groupedRules.put(length, new ArrayList<List<String>>());
                    }
                    groupedRules.get(length).add(categorySeq);
                }  
            }
            
            //While loop iterates over ngrams
            String inline;
            BufferedReader reader=null;
            BufferedWriter writer=null;
            try
            {
            reader=new BufferedReader(new InputStreamReader(new FileInputStream(new File(ngramsFile)),Charset.forName("UTF-8") ));
            writer = new BufferedWriter( new OutputStreamWriter(System.out,"UTF-8") );
                while((inline=reader.readLine())!=null)
                {
                    //Parse ngrams
                    String ngramsStr=null;
                    boolean validLine=false;
                    if(inline.matches("^\\dGRAM.*"))
                    {
                        ngramsStr=inline.substring("GRAM".length()+1);
                        validLine=true;
                    }
                    else if(inline.matches("^WORD.*")){
                        ngramsStr=inline.substring("WORD".length());
                        validLine=true;
                    }
                     if(DEBUG){
                        System.err.println("Processing n-gram line: "+inline);
                     }
                    if(validLine){
                        if(DEBUG){
                        System.err.println("Is valid");
                        }
                        if(ngramsStr!=null)
                        {
                             if(DEBUG){
                            System.err.println("NgramsStr is OK");
                             }
                            boolean incorrectWordFoundinNgram=false;
                            List<List<String>> ngramListRepr = new ArrayList<List<String>>();
                            String[] ngramsArray= ngramsStr.split("---",-1);
                            for(String word: ngramsArray)
                            {
                                word=word.trim();
                                List<String> wordStringRepresentation = WordsTrie.getTrieListFromLexicalForm(word, true);
                                if(wordStringRepresentation == null){
                                    incorrectWordFoundinNgram=true;
                                    break;
                                }
                                ngramListRepr.add(wordStringRepresentation);
                            }
                            
                             if(DEBUG){
                            System.err.println("Incorrect word found: "+Boolean.toString(incorrectWordFoundinNgram));
                             }
                            if(!incorrectWordFoundinNgram){
                                
                                
                                //Once ngram has been parsed, we iterate over all the rules with the same length as the ngram
                                //TO DO: be careful with case
                                int ngramLength = ngramListRepr.size();
                                if( groupedRules.containsKey(ngramLength) ){
                                    
                                    if(DEBUG){
                                        System.err.println("Checkig rules for ngram "+ngramsStr+" with length: "+Integer.toString(ngramLength));
                                    }
                                    
                                    //Check whether any rule matches our ngram
                                    for(List<String> catSequence: groupedRules.get(ngramLength)){
                                        if(DEBUG){
                                            System.err.println("  Checkig category sequence: "+Util.join(catSequence, "#"));
                                        }
                                        boolean valid=true;
                                        for(int i=0; i< catSequence.size(); i++){
                                            if( !phraseGenerator.getCategoriesTries().get(catSequence.get(i)).containsElement(ngramListRepr.get(i)) ){
                                                valid=false;
                                                if(DEBUG){
                                                    System.err.println("    Invalid at position "+Integer.toString(i)+" because "+Util.join(ngramListRepr.get(i), "#")+" not found in "+catSequence.get(i));
                                                }
                                                break;
                                            }
                                        }
                                        if(valid){
                                            //Valid ngram: print IT!!!!!!
                                            System.err.println("    Valid!");
                                            writer.write(Util.joinArray(ngramsArray, " ").trim()+"\n");

                                        }
                                    }
                                }
                                else
                                 if(DEBUG){
                                        System.err.println("We have not groups for length: "+Integer.toString(ngramLength));
                                    }
                            }
                        }
                        
                    }
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
                
                if(writer != null)
                    try{
                        writer.close();
                    } catch(Exception e){}
            }
            
            
            
            //Generate phrases
            //This shouln't be done
            /*
            PhraseGenerator phraseGenerator=new PhraseGenerator(transfer,wordsTrie);
            BufferedWriter writer = new BufferedWriter( new OutputStreamWriter(System.out,"UTF-8") );
            phraseGenerator.generatePhrases(writer, nGramTrie,ngramOrder);
            writer.close();
                    */
        }
        else if (line.hasOption("x"))
        {
            //Loading rules
            File f = new File(rulesFile);
            JAXBContext context = JAXBContext.newInstance(Interchunk.class);
            Unmarshaller u = context.createUnmarshaller();
            Interchunk interchunk = (Interchunk) u.unmarshal(f);

            List<NGramTrie> ngramTries= new LinkedList<NGramTrie>();

            if(numNGramsFiles<=0)
            {
                //Load bigrams and trigrams
                NGramTrie nGramTrie=new NGramTrie();
                nGramTrie.loadFromFile(new File(ngramsFile));
                ngramTries.add(nGramTrie);
            }
            else
            {
                for(int i=1; i<=numNGramsFiles; i++)
                {
                    NGramTrie nGramTrie=new NGramTrie();
                    nGramTrie.loadFromFile(new File(ngramsFile+Integer.toString(i)));
                    ngramTries.add(nGramTrie);
                }
            }

            //Load lexical forms
            ChunksTrie chunksTrie=new ChunksTrie(generateAlignments);
            chunksTrie.loadFromFile(new File(lexformsFile));

            int numLine=1;
            BufferedWriter writer = new BufferedWriter( new OutputStreamWriter(System.out,"UTF-8") );
            for(NGramTrie nGramTrie: ngramTries)
            {
                System.err.println("Genrating line "+Integer.toString(numLine)+" of "+Integer.toString(ngramTries.size()));
                ChunksTrie filteredChunks= chunksTrie.filterGivenSources(nGramTrie);
                
                ChunkPhraseGenerator phraseGenerator=new ChunkPhraseGenerator(interchunk,filteredChunks,generateAlignments);
                //phraseGenerator.generatePhrases(writer,nGramTrie,ngramOrder);
                phraseGenerator.generatePhrasesStrict(writer,nGramTrie,ngramOrder);
                numLine++;
            }
            writer.close();
            
        }
        else if (line.hasOption("p"))
        {
            System.err.println("Reverse pretransfer option selected");
            BufferedWriter writer = new BufferedWriter( new OutputStreamWriter(System.out,"UTF-8") );
            InputStreamReader reader= new InputStreamReader(System.in,"UTF-8");

            ReversePreTransfer rpt=new ReversePreTransfer();

            System.err.print("Loading forms split by pretransfer... ");
            rpt.loadFromFile(new File(splitFile));
            System.err.println("OK");

            System.err.print("Processing input... ");
            rpt.reverse(reader, writer,generateAlignments);
            System.err.println("OK");

            reader.close();
            writer.close();
        }

    }
}
