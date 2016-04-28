/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package es.ua.dlsi.hybridmt.apertiumphrasegenerator.trie;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map.Entry;
import java.util.Set;

/**
 *
 * @author vmsanchez
 */
public class Trie<T> {

    private Node<T> root;


    public Trie(T rootData)
    {
        root = new Node<T>(rootData);
    }

    public int insertElement(List<T> element)
    {
        int createdNodes=0;
        Node<T> curNode=root;
        for(T el : element)
        {
            if(curNode.children.containsKey(el))
                curNode=curNode.children.get(el);
            else
            {
                createdNodes++;
                Node<T> newNode=new Node<T>(el);
                curNode.children.put(el, newNode);
                curNode=newNode;
            }
        }
        return createdNodes;
    }

    public void merge(Trie<T> trie)
    {
        mergeNodes(root, trie.root);
    }

    private void mergeNodes(Node<T> existingNode, Node<T> newNode)
    {
        for(Entry<T,Node<T>> entry: newNode.children.entrySet())
        {
            if(existingNode.children.containsKey(entry.getKey()))
            {
                mergeNodes( existingNode.children.get(entry.getKey()),entry.getValue() );
            }
             else
            {
                existingNode.children.put(entry.getKey(), entry.getValue());
            }
        }
    }

   public List<List<T>> getItemList()
   {
       return getItemList(root);

   }

   private List<List<T>> getItemList(Node<T> node)
   {
       List<List<T>> itemList= new LinkedList<List<T>>();
        if(node.children.isEmpty())
        {
            List<T> item= new LinkedList<T>();
            item.add(node.getData());
            itemList.add(item);
            return itemList;
        }
        else
        {
            for(Node<T> child: node.children.values())
            {
                itemList.addAll(getItemList(child));
            }
            for(List<T> list: itemList)
            {
                list.add(0, node.getData());
            }
        }
        return itemList;
   }

    public boolean isElement(List<T> element)
    {
        boolean found=true;
        Node<T> curNode=root;
        for(T el : element)
        {
            if(curNode.children.containsKey(el))
            {
                curNode=curNode.children.get(el);
            }
            else
            {
                found=false;
                break;
            }
        }
        return found;
    }

    public Node<T> getNode(List<T> element)
    {
        boolean found=true;
        Node<T> curNode=root;
        for(T el : element)
        {
            if(curNode.children.containsKey(el))
            {
                curNode=curNode.children.get(el);
            }
            else
            {
                found=false;
                break;
            }
        }
        if (found)
            return curNode;
        else
            return null;
    }

    public Trie<T> getSubTrie(List<T> element, T startingData)
    {
        Trie<T> subTrie= new Trie<T>(startingData);
        
        Node<T> curNode=root;
        Node<T> curNodeSubtrie=subTrie.root;

        boolean found=true;
        for(T el : element)
        {
            if(curNode.children.containsKey(el))
            {
                curNode=curNode.children.get(el);

                Node<T> newNode=new Node<T>(el);
                curNodeSubtrie.children.put(el, newNode);
                curNodeSubtrie=newNode;
            }
            else
            {
                found=false;
                break;
            }
        }
        if (!found)
            return null;

        for(Entry<T,Node<T>> entry: curNode.children.entrySet())
        {
            curNodeSubtrie.children.put(entry.getKey(), entry.getValue().copy());
        }
        
        return subTrie;
    }

    
    public void pruneLeaves(Set<T> allowedLeaves) {
        pruneLeaves(allowedLeaves, 0);
    }


    public void pruneLeaves(Set<T> allowedLeaves, int distanceToLeave) {
        List<Node<T>> path=new ArrayList<Node<T>>();
        path.add(root);
        pruneLeaves(allowedLeaves,path, distanceToLeave);
    }

    private boolean pruneLeaves(Set<T> allowedLeaves,List<Node<T>> pathFromRoot, int distanceToLeaf)
    {
        Node<T> currentNode=pathFromRoot.get(pathFromRoot.size()-1);
        Node<T> leafNode=currentNode;

        boolean pathFound=true;
        for(int i=0; i< distanceToLeaf; i++)
        {
            if(leafNode.children.size()>=1)
                leafNode=leafNode.children.values().iterator().next();
            else
            {
                pathFound=false;
                break;
            }
        }

       
        if(leafNode.children.isEmpty())
        {

            //Leaf node

            if (pathFound)
            {
                if(allowedLeaves.contains(currentNode.getData()))
                    return false;
                else
                    return true;
            }
            else
                return false;
        }
        else
        {
            //Not leaf

            Set<T> nodesToRetain=new HashSet<T>();
            for(Entry<T,Node<T>> entry: currentNode.children.entrySet())
            {
                pathFromRoot.add(entry.getValue());
                boolean deleteIt=pruneLeaves(allowedLeaves,pathFromRoot, distanceToLeaf);
                if (!deleteIt)
                    nodesToRetain.add(entry.getKey());
                pathFromRoot=pathFromRoot.subList(0, pathFromRoot.size()-1);
            }

            Set<T> nodesToRemove= new HashSet<T>(currentNode.children.keySet());
            nodesToRemove.removeAll(nodesToRetain);
            for (T keyToRemove: nodesToRemove)
            {
                currentNode.children.remove(keyToRemove);
            }

            return false;
        }
        
     
    }

}

