/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */



import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.TreeMap;

/**
 *
 * @author jun
 */
public class AnnFromMedEx {

    /**
     * @param args the command line arguments
     */

    public static void main(String[] args) {

        // String inDir = "/mnt/c/Users/ilall/CSCI230/AnnFromMedEx/input/*.txt";
        // String outDir = "/mnt/c/Users/ilall/CSCI230/AnnFromMedEx/medex_ann/";
        
        String inDir = args[0];
        String outDir = args[1];
        
        HashMap<Integer, String> tMap = new HashMap<>();
        tMap.put(1, "Drug");
        tMap.put(3, "Form");
        tMap.put(4, "Strength");
        tMap.put(5, "Dosage");
        tMap.put(6, "Route");
        tMap.put(7, "Frequency");
        tMap.put(8, "Duration");
        tMap.put(9, "Frequency"); //Neccessity
        
        //1 Drug
        //3 Form
        //4 Strength
        //5 Dosage
        //6 Route
        //7 Frequency
        //8 Duration
        //9 Frequency
        
        //cf. Neccessity     (e.g. 'prn[10, 13]')
        
        ArrayList<String> fileList = new ArrayList<String>();
        listFile(inDir, fileList, "txt");
        
        for (String f : fileList) {
            ArrayList<String> outs = new ArrayList<>();            
            parse(inDir, f, tMap, outDir, outs);
            writeListFile(outDir + f.replace(".txt", ".ann"), outs);
        }
    }

    public static void parse(String inDir, String fileName, 
            HashMap<Integer, String> tMap, String outDir, 
            ArrayList<String> outs) {
        
        TreeMap<Integer, Integer> sMap = new TreeMap<>();
        HashMap<Integer, Integer> sEMap = new HashMap<>();
        HashMap<Integer, String> sTMap = new HashMap<>();
        HashMap<Integer, String> sSMap = new HashMap<>();
        int sI = 1;

        HashMap<Integer, ArrayList<String>> rList = new HashMap<>();
        
        String str = "";
        BufferedReader txtin = null;
        try {
            txtin = new BufferedReader(new FileReader(inDir + fileName));

            //62	4. Atenolol 50 mg b.i.d.|Atenolol[5816,5824]|||50mg[5825,5830]|||b.i.d.[5831,5837]|||C0983889|315438|1202|atenolol
            while ((str = txtin.readLine()) != null) {
                if (str.endsWith("|")) {
                    str += "AA";
                }
                str = str.split("\t", 2)[1];
                
                String s[] = str.split("\\|");
                if (s.length != 14) {
                    //System.out.println(str);
                    str = str.replace("| ", " ");
                    
                }
                s = str.split("\\|");
                if (s.length != 14) {
                    System.out.println(str);
                }

                HashSet<Integer> relSet = new HashSet<>();
                int med = -1; 
                for (int i = 0; i < s.length; i++) {
                    if (!tMap.containsKey(i)) {
                        continue;
                    }                    
                    if (s[i].trim().isEmpty()) {
                        continue;
                    }
                    // no span info
                    if (!s[i].contains("[")) {
                        continue;
                    }
                    int bQ = s[i].lastIndexOf("[");
                    String sS[] = s[i].substring(bQ).replace("[", "").replace("]", "").split(",");
                    int b = Integer.parseInt(sS[0]);
                    int e = Integer.parseInt(sS[1]);
                    
                    if (!sMap.containsKey(b)) {
                        sMap.put(b, sI);
                        sEMap.put(b, e);
                        sTMap.put(b, tMap.get(i));
                        String conStr = s[i].substring(0, s[i].indexOf("[")).toLowerCase();  
                        sSMap.put(b, conStr);
                        
                        sI++;                        
                    } else {
                        //possible
                        //System.out.println("dupp!!!!: " + fileName + " " + b + " " + e + " " + str);
                    }                    
                    
                    if (i == 1) {
                        med = b;
                    } else {
                        relSet.add(b);
                    }                    
                }                    

                String th2 = sTMap.get(med);
                for (int b : relSet) {
                    String th1 = sTMap.get(b);
                    String relStr = th1 + "-" + th2 + " Arg1:T" + sMap.get(b) + " Arg2:T" + sMap.get(med);
                    //System.out.println(relStr);
                    
                    // get the later T number
                    int rListKey = Math.max(sMap.get(b), sMap.get(med));
                    
                    if (!rList.containsKey(rListKey)) {
                        ArrayList<String> rels = new ArrayList<>();
                        rels.add(relStr);
                        rList.put(rListKey, rels);
                    } else {
                        rList.get(rListKey).add(relStr);                       
                    }
                }
            }
            
            int rI = 1;
            for (int b : sMap.keySet()) {
                int tI = sMap.get(b);
                //T43	Drug 6573 6578	lasix
                String tT = sTMap.get(b);
                int e = sEMap.get(b);
                  
                String toutStr = "T" + tI + "\t" + tT + " " + b + " " + e + "\t" + sSMap.get(b);
                //System.out.println(toutStr);
                outs.add(toutStr);
                //add to out
                if (rList.containsKey(tI)) {
                    ArrayList<String> rels = rList.get(tI);
                    for (String rel : rels) {
                        //System.out.println("R" + rI + "\t" + rel);
                        //add to out
                        outs.add("R" + rI + "\t" + rel);
                        rI++;
                    }
                }
            }
            
            //System.out.println("--------------------------------------------");
            
        } catch (Exception ex) {
            ex.printStackTrace();
        } finally {
            try {
                txtin.close();
            } catch (Exception ex) {

           }
        }
    }

    public static void listFile(String dirName, ArrayList<String> fileList, String ext) {
        File dir = new File(dirName);

        String[] children = dir.list();
        if (children == null) {
            return;
        } else {
            for (int i = 0; i < children.length; i++) {
                // Get filename
                String filename = children[i];
                if (filename.endsWith("." + ext)) {
                    fileList.add(filename);
                }
            }
        }

    }
    
    public static PrintWriter getPrintWriter (String file)
    throws IOException {
        return new PrintWriter (new BufferedWriter
                (new FileWriter(file)));
    }

    public static void writeListFile(String name, ArrayList<String> outs) {

        try {

            PrintWriter out = getPrintWriter(name);
            for (String str : outs) {
                out.println(str);
            }
            out.flush();
            out.close();
        } catch (IOException e) {
            e.printStackTrace ();
        }
        //System.out.println(idx.size());
    }
    
    public static String purgeString(String in) {
        StringBuffer out = new StringBuffer(); // Used to hold the output.
        char c; // Used to reference the current character.

        if (in == null || ("".equals(in))) return ""; // vacancy test.
        for (int i = 0; i < in.length(); i++) {
            c = in.charAt(i); // NOTE: No IndexOutOfBoundsException caught here; it should not happen.
            if (Character.isAlphabetic(c) || Character.isDigit(c)) {
                out.append(c);
            } else {
                out.append(" ");                
            }
        }
        return out.toString();
    }        
}