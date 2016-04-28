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
public class MultiChunk {
    private List<List<String>> chunks;
    private String source;

    public MultiChunk(List<List<String>> chunks, String source) {
        this.chunks = chunks;
        this.source = source;
    }

    public List<List<String>> getChunks() {
        return chunks;
    }

    public void setChunks(List<List<String>> chunks) {
        this.chunks = chunks;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    

}
