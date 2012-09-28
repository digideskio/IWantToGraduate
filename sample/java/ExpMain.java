package org.uw.course;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.StatusLine;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONException;
import org.json.JSONObject;

public class ExpMain {
    public static void main(String[] args){
        
        DefaultHttpClient httpclient = new DefaultHttpClient();
        HttpResponse response = null;
//        HttpPost httpPost = new HttpPost("http://sdb.admin.washington.edu/timeschd/public/genedinq.asp");
        HttpPost httpPost = new HttpPost("http://localhost/course_req/api?");
        
        try {
            httpPost.setEntity(setupEntity());
            response = httpclient.execute(httpPost);
            String res = retrieveResponse(response);
            System.out.println("res: " + res);
        } catch (ClientProtocolException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        
    }
    
    
    private static StringEntity setupEntity() throws UnsupportedEncodingException{
        
        
        
//        List<NameValuePair> entity = new ArrayList<NameValuePair>();
        JSONObject jEntity = new JSONObject();
        try {
            //specify the quarter and the year try to search
            jEntity.append("QTRYR", "AUT 2012");
            
            /*
             * 1: Visual, Literary & Performing Arts Courses (VLPA)
             * 2: Individual and Society Courses (I&S)
             * 3: Nature World Courses (NW)
             * 4: Writing Courses (W)
             * 5: English Composition Courses (C)
             * 6: Quantitative, Symbolic or Formal Reasoning Courses (QSR)
             */
            jEntity.append("REQ", "1");
            
            //time has to be in the format like 0830 which stands for 8:30am
            
            //this stands for the start time of the class has to be later than 08:30am
            //this number has the range between 0830 to 1900. Only support 0830, 0900, 0930..., do not use 0920 or something like that
            jEntity.append("STARTTIME", "0830");
            
            //this stands for the end time of the class has to be earlier than 18:30
            //this number has range between 0930 to 2000. ends with 30 or 00
            jEntity.append("ENDTIME", "1830");
            
            //the course has to have credits more than or equal to 0
            //this number has range 0-5, 0 stands for any credit range(which means the user 
            //doesn't care about credit the course has)
            jEntity.append("STARTCREDIT", "0");
            
            //the course has to have credits less than or equal to 25
            //this number has range 0-5, 0 stands for any credit range(which means the user 
            //doesn't care about credit the course has)

            jEntity.append("ENDCREDIT", "5");
            
            //the course number can be 000, 100, 200, 300, 400
            //000 stands for any
            jEntity.append("STARTCOURSE", "000");
            
            //the course number can be 000, 199, 299, 399, 499
            //000 stands for any
            jEntity.append("ENDCOURSE", "499");
            
            //three campus supported. If you want to search in this campus, set the value to be true,
            //otherwise, set the value to false or do not include this key-value pair
            jEntity.append("SEATTLE", true);
            jEntity.append("BOTHELL", false);
//            jEntity.append("TACOMA", false);

            
            /*
             * IMPORTANT: things get tricky here
             * Since the searching takes super long time, the uw webpage only returns 20 courses per page. 
             * If there are more courses in next page, the json string my server returns contains an 
             * element: "hasNextPage":true, otherwise, the value if false. So you can tell whether there is
             * next page or not based on the boolean value of this key.
             * If you want to get next page, what you can do it set "NEXTPAGE" below to be true, then, find
             * the last course that my server returned, in the sample above the course 
             * is ("courseTitle":"INTERMEDIATE TAGALOG (VLPA)"), and set "NEXTSLN" to be this course's sln, 
             * "NEXTTIME" to be the start time of this course
             */
            jEntity.append("NEXTPAGE", true);
            jEntity.append("NEXTSLN", "20254");
            jEntity.append("NEXTTIME", "0930");
            
            /*
             * few searching options are available, you can exclude some courses:
             * a. courses with entry code: "ENTRYCODE"
             * b. courses has pre-request: "PREREQCODE"
             * c. course has registration restrictions: "REGRESCODE", 
             * 
             * if you prefer to exclude these courses, set the value to be true or do
             * not include this key-value pair
             */
            jEntity.append("ENTRYCODE", true);
            jEntity.append("PREREQCODE", false);
            jEntity.append("REGRESCODE", true);
            
            
        } catch (JSONException excp) {
            excp.printStackTrace();
        }
        
        
        return new StringEntity(jEntity.toString());
    }
    
    /*
     * retrieves the message from http response
     */
    private static String retrieveResponse(HttpResponse response) throws IllegalStateException, IOException{
        StatusLine statusLine = response.getStatusLine();
        int statusCode = statusLine.getStatusCode();
        boolean success  = false;
        StringBuilder builder = new StringBuilder();
        if (statusCode == 200) {//status correct
            success = true;
            HttpEntity entity = response.getEntity();
            InputStream content = entity.getContent();
            BufferedReader reader = new BufferedReader(new InputStreamReader(content));
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
            }
        } else {
            throw new ClientProtocolException("failed to download feed");
        }
        return success ? builder.toString() : null;
    }
}
