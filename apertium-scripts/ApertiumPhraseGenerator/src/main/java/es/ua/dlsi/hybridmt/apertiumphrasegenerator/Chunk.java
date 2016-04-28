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
public abstract class Chunk {
    protected String chunk;

    public Chunk(String chunk) {
        this.chunk = chunk;
    }


    public String getChunk() {
        return chunk;
    }

    public void setChunk(String chunk) {
        this.chunk = chunk;
    }

   
    

}
