/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

/**
 *
 * @author vmsanchez
 */
public class ChunkFragment extends Chunk {

    private int id;
    private int number;
    private boolean isLast;

    public ChunkFragment(String chunk,int id, int number, boolean isLast) {
        super(chunk);
        this.id=id;
        this.number = number;
        this.isLast = isLast;
    }

    public boolean isIsLast() {
        return isLast;
    }

    public void setIsLast(boolean isLast) {
        this.isLast = isLast;
    }

    public int getNumber() {
        return number;
    }

    public void setNumber(int number) {
        this.number = number;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

}
