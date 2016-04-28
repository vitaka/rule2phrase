/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import java.util.regex.Pattern;

/**
 *
 * @author vmsanchez
 */
public class ReplacementPattern {
    private Pattern pattern;
    private String source;
    private String replacement;
    private int numSourceWords;

    public ReplacementPattern(String source, int numSourceWords, String replacement) {
        this.source = source;
        this.replacement = replacement;
        this.pattern = Pattern.compile(Pattern.quote(source));
        this.numSourceWords=numSourceWords;
    }

    public Pattern getPattern() {
        return pattern;
    }

    public void setPattern(Pattern pattern) {
        this.pattern = pattern;
    }

    public String getReplacement() {
        return replacement;
    }

    public void setReplacement(String replacement) {
        this.replacement = replacement;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public int getNumSourceWords() {
        return numSourceWords;
    }

    public void setNumSourceWords(int numSourceWords) {
        this.numSourceWords = numSourceWords;
    }

    

    
}
