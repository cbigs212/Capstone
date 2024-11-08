//package JavaNative.KNucleo;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.SortedSet;
import java.util.TreeSet;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class knucleo {
static ArrayList<Callable< Map<ByteString, ByteString> > > createFragmentTasks(final byte[] sequence, int[] fragmentLengths) {
	ArrayList<Callable<Map<ByteString, ByteString>>> tasks = new ArrayList<Callable<Map<ByteString, ByteString>>>();
	for (int fragmentLength : fragmentLengths) {
	    for (int index=0; index<fragmentLength; index++) {
		final int offset = index;
		final int finalFragmentLength = fragmentLength;
		tasks.add(new Callable<Map<ByteString, ByteString>>() {
		    public Map<ByteString, ByteString> call() {
			return createFragmentMap(sequence, offset, finalFragmentLength);
		    }
		});
	    }
	}
	return tasks;
    }
    	
    static Map<ByteString, ByteString> createFragmentMap(byte[] sequence, int offset, int fragmentLength) {
	HashMap<ByteString, ByteString> map = new HashMap<ByteString, ByteString>();
	int lastIndex = sequence.length - fragmentLength + 1;
	ByteString key = new ByteString(fragmentLength);	
	for (int index=offset; index<lastIndex; index+=fragmentLength) {
	    key.calculateHash(sequence, index);
	    ByteString fragment = map.get(key);
	    if (fragment != null) {
		fragment.count++;
	    } else {
		map.put(key, key);
		key = new ByteString(fragmentLength);
	    }
	}

	return map;
    }
        
    // Destructive!
    static Map<ByteString, ByteString> sumTwoMaps(Map<ByteString, ByteString> map1, Map<ByteString, ByteString> map2) {
	for (Map.Entry<ByteString, ByteString> entry : map2.entrySet()) {
	    ByteString sum = map1.get(entry.getKey());
	    if (sum != null)
		sum.count += entry.getValue().count;
	    else
		map1.put(entry.getKey(), entry.getValue());
	}
	return map1;
    }
    
    static String writeFrequencies(float totalCount, Map<ByteString, ByteString> frequencies) {
	SortedSet<ByteString> list = new TreeSet<ByteString>(frequencies.values());
	StringBuilder sb = new StringBuilder();
	for (ByteString k : list)
	    sb.append(String.format("%s %.3f\n", k.toString().toUpperCase(), (float)(k.count) * 100.0f / totalCount));
	
	return sb.append('\n').toString();
    }
    
    static String writeCount(List<Future<Map<ByteString, ByteString>>> futures, String nucleotideFragment) throws Exception {
	ByteString key = new ByteString(nucleotideFragment.length());
	key.calculateHash(nucleotideFragment.getBytes(), 0);
	
	int count = 0;
	for (Future<Map<ByteString, ByteString>> future : futures) {
	    ByteString temp = future.get().get(key);
	    if (temp != null) count += temp.count;
	}
	
	return count + "\t" + nucleotideFragment.toUpperCase() + '\n';
    }
    
    public static void main (String[] args) throws Exception {
	String line;
	BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
	while ((line = in.readLine()) != null) {
	    if (line.startsWith(">THREE")) break;
	}
	    
	ByteArrayOutputStream baos = new ByteArrayOutputStream();
        byte bytes[] = new byte[100];
        while((line = in.readLine()) != null) {
	    if (line.length() > bytes.length)
		bytes = new byte[line.length()];
	    
	    int i;
	    for(i=0; i<line.length(); i++)
		bytes[i] = (byte)line.charAt(i);
	    baos.write(bytes, 0, i);
        }
	
	byte[] sequence = baos.toByteArray();
		
	ExecutorService pool = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
	int[] fragmentLengths = { 1, 2, 3, 4, 6, 12, 18 };
	List<Future<Map<ByteString, ByteString>>> futures = pool.invokeAll(createFragmentTasks(sequence, fragmentLengths));
	pool.shutdown();
	
	StringBuilder sb = new StringBuilder();

	sb.append(writeFrequencies(sequence.length, futures.get(0).get()));
	sb.append(writeFrequencies(sequence.length - 1, sumTwoMaps(futures.get(1).get(), futures.get(2).get())));
	
	String[] nucleotideFragments = { "ggt", "ggta", "ggtatt", "ggtattttaatt", "ggtattttaatttatagt" };
	for (String nucleotideFragment : nucleotideFragments) {
	    sb.append(writeCount(futures, nucleotideFragment));
	}
	
	System.out.print(sb.toString());	
    }
    
    static final class ByteString implements Comparable<ByteString> {
        public int hash, count=1;
        public final byte bytes[];
	
        public ByteString(int size) {
            bytes = new byte[size];
        }
	
        public void calculateHash(byte k[], int offset) {
	    int temp = 0;
            for (int i=0; i<bytes.length; i++) {
		byte b = k[offset+i];
                bytes[i] = b;
                temp = temp * 31 + b;
            }
	    hash = temp;
        }
	
        public int hashCode() {
            return hash;
        }
	
        public boolean equals(Object obj) {
	    return Arrays.equals(bytes, ((ByteString)obj).bytes);
        }
	
        public int compareTo(ByteString other) {
            return other.count - count;
        }
	
	public String toString() {
	    return new String(bytes);
	}
    }
}
