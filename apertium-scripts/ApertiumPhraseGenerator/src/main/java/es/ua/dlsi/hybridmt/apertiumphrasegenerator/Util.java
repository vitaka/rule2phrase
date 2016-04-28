/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import java.util.Iterator;
import java.util.List;
import java.util.regex.Pattern;

/**
 *
 * @author vmsanchez
 */
public class Util {
    public static String join(List<String> s, String delimiter) {
    if (s == null || s.isEmpty()) return "";
    Iterator<String> iter = s.iterator();
    StringBuilder builder = new StringBuilder(iter.next());
    while( iter.hasNext() )
    {
        builder.append(delimiter).append(iter.next());
    }
    return builder.toString();
}
    
    public static String joinArray(String[] s, String delimiter) {
    if (s == null || s.length == 0) return "";
    StringBuilder builder = new StringBuilder();
    for(int i=0; i<s.length;i++)
    {
        if(i> 0)
            builder.append(delimiter);
        builder.append(s[i]);
    }
    return builder.toString();
}
    
     public static String joinChunks(List<TrueChunk> s, String delimiter) {
    if (s == null || s.isEmpty()) return "";
    Iterator<TrueChunk> iter = s.iterator();
    StringBuilder builder = new StringBuilder(iter.next().getChunk());
    while( iter.hasNext() )
    {
        builder.append(delimiter).append(iter.next().getChunk());
    }
    return builder.toString();
}

     public static String joinChunksf(List<ChunkFragment> s, String delimiter) {
    if (s == null || s.isEmpty()) return "";
    Iterator<ChunkFragment> iter = s.iterator();
    StringBuilder builder = new StringBuilder(iter.next().getChunk());
    while( iter.hasNext() )
    {
        builder.append(delimiter).append(iter.next().getChunk());
    }
    return builder.toString();
}

      public static String joinSources(List<TrueChunk> s, String delimiter) {
    if (s == null || s.isEmpty()) return "";
    Iterator<TrueChunk> iter = s.iterator();
    StringBuilder builder = new StringBuilder(iter.next().getSource());
    while( iter.hasNext() )
    {
        builder.append(delimiter).append(iter.next().getSource());
    }
    return builder.toString();
}

     public static Pair<String> splitSourceAndTransfer(String src)
    {
         Pair<String> value=null;
         String[] pieces=src.split(Pattern.quote(" ||| "));
         if(pieces.length==2)
         {
            value=new Pair<String>(pieces[0].trim(), pieces[1].trim());
         }
         return value;
     }

    static String joinTransferDebug(List<TrueChunk> s, String delimiter) {
        if (s == null || s.isEmpty()) return "";
    Iterator<TrueChunk> iter = s.iterator();
    StringBuilder builder = new StringBuilder(iter.next().getDebugTransfer());
    while( iter.hasNext() )
    {
        builder.append(delimiter).append(iter.next().getDebugTransfer());
    }
    return builder.toString();
    }

    static String lowercaseApertiumWord(String apword)
    {
        StringBuilder builder=new StringBuilder(apword.trim());
        builder.setCharAt(1, Character.toLowerCase(builder.charAt(1)));
        return builder.toString();
    }
}
