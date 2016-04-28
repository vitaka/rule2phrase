/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author vmsanchez
 */
public class TrueChunk extends Chunk {

    private String source;
    private List<String> sourceWords;
    private String debugTransfer;

     public TrueChunk(String chunk, String source) {
        super(chunk);
        build( source, null);
    }

     public TrueChunk(String chunk, String source, String dt) {
         super(chunk);
        build( source, dt);
    }

      private void build( String source, String dt)
    {
        this.source = source;
        sourceWords=new ArrayList<String>();
        //System.err.println("parsing "+source);
        debugTransfer=dt;

        sourceWords=parseSourceWords(source);

    }

     public static List<String> parseSourceWords(String source)
    {
        int pos,prevPos;
        List<String> parsedList=new ArrayList<String>();
        prevPos=0;
        pos=source.indexOf("^",prevPos);
        while(pos>=0)
        {
            String w=source.substring(prevPos, pos).trim();
            if(w.length()>0)
                parsedList.add(w.intern());

            prevPos=pos;
            pos=source.indexOf("^",prevPos+1);
        }
        String w=source.substring(prevPos).trim();
        if(w.length()>0)
            parsedList.add(w.intern());
        return parsedList;
    }

       public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public List<String> getSourceWords() {
        return sourceWords;
    }

    public String getDebugTransfer() {
        return debugTransfer;
    }

    public void setDebugTransfer(String debugTransfer) {
        this.debugTransfer = debugTransfer;
    }

}
