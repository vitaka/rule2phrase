/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator.trie;

import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

/**
 *
 * @author vmsanchez
 */
public class Node<T> {
    T data;
    Map<T,Node<T>> children;

    public Node(T basedata)
    {
        data = basedata;
        children= new HashMap<T,Node<T>>();
    }

    public Map<T, Node<T>> getChildren() {
        return children;
    }

    public void setChildren(Map<T, Node<T>> children) {
        this.children = children;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }

    public Node<T> copy()
    {
        Node<T> copy= new Node<T>(data);
        for(Entry<T,Node<T>> entry: children.entrySet())
        {
            copy.children.put(entry.getKey(), entry.getValue().copy());
        }
        return copy;
    }
    
}
