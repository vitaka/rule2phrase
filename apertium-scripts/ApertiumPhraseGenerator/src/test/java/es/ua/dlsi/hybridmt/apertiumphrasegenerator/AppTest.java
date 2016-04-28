package es.ua.dlsi.hybridmt.apertiumphrasegenerator;

import es.ua.dlsi.hybridmt.apertiumphrasegenerator.trie.Trie;
import java.util.ArrayList;
import java.util.List;
import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

/**
 * Unit test for simple App.
 */
public class AppTest 
    extends TestCase
{
    /**
     * Create the test case
     *
     * @param testName name of the test case
     */
    public AppTest( String testName )
    {
        super( testName );
    }

    /**
     * @return the suite of tests being tested
     */
    public static Test suite()
    {
        return new TestSuite( AppTest.class );
    }

    /**
     * Rigourous Test :-)
     */
    public void testApp()
    {
        assertTrue( true );
    }

    public void testTrie()
    {
        Trie<String> trie = new Trie<String>("");
        int createdNodes;

        List<String> l1= new ArrayList<String>();
        l1.add("a");
        l1.add("b");
        l1.add("c");
        createdNodes=trie.insertElement(l1);
        assertEquals(3, createdNodes);

        List<String> l2=new ArrayList<String>();
        l2.add("a");
        l2.add("d");
        createdNodes=trie.insertElement(l2);
        assertEquals(1, createdNodes);

        assertTrue(trie.isElement(l1));
        assertTrue(trie.isElement(l2));
           
        List<String> l3=new ArrayList<String>();
        l3.add("a");
        l3.add("b");
        assertTrue(trie.isElement(l3));

        List<String> l4=new ArrayList<String>();
        l4.add("a");
        l4.add("c");

        assertFalse(trie.isElement(l4));



        
    }
}
