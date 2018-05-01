package tests;

import client.model.*;

import client.serde.StatisticsDeserializer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import javafx.util.Pair;
import org.apache.commons.lang3.builder.ReflectionToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;

import javax.xml.crypto.dsig.keyinfo.KeyValue;
import java.io.File;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

public class Test {


    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper(new YAMLFactory());

        try {

            OATSConfigReader confReader = mapper.readValue(new File("/home/nvinzens/Desktop/OATS/config.yaml"), OATSConfigReader.class);

            OATSConfig config = new OATSConfig(confReader);
            System.out.println(config.getKafkaTopic());
            System.out.println(config.getEvent());
            System.out.println(config.getOperator());
            System.out.println(config.getThreshold());
            for (String xpath : config.getXpaths()) System.out.println(xpath);

//            for (Map<String, Object> map : confReader.getSubscriptions()) {
//                Map<String, Object> subscription = (Map) map.get("subscription");
//                System.out.print(subscription.toString());
//                for (Map.Entry<String, Object> entry : subscription.entrySet()) {
//                    //System.out.println(entry.getKey() + ": " + entry.getValue());
//                    if (entry.getKey().equals("kafka_publish_topic")) System.out.println("kafka_publish_topic: " + entry.getValue());
//                    if (entry.getKey().equals("kafka_streams_eval")) {
//                        System.out.println("evaluate: " + entry.getValue());
//                    }
//                    if (entry.getKey().equals("event_threshold")) {
//                        List<Map<String, Object>> threshList = (List) entry.getValue();
//                        for (Map<String, Object> threshMap : threshList) {
//                            for (Map.Entry<String, Object> threshEntry: threshMap.entrySet()) {
//                                if (threshEntry.getKey().equals("value")) System.out.println("value: " + threshEntry.getValue());
//                                if (threshEntry.getKey().equals("operator")) {
//                                    Operator op = Operator.getOperator((String) threshEntry.getValue());
//                                    switch (op) {
//                                        case GREATER_THAN:
//                                            System.out.println("operator: >");
//                                    }
//                                }
//                                if (threshEntry.getKey().equals("kafka_event_topic")) System.out.println("kafka_event_topic: " + threshEntry.getValue());
//                                if (threshEntry.getKey().equals("event")) System.out.println("event: " + threshEntry.getValue());
//                                if (threshEntry.getKey().equals("data_fields")) {
//                                    List<Map<String, String>> xpaths = (List) threshEntry.getValue();
//                                    for (Map<String, String> xpathMap : xpaths) {
//                                        for (Map.Entry<String, String> xpath : xpathMap.entrySet()) {
//                                            System.out.println("xpath: " + xpath.getValue());
//                                        }
//                                    }
//                                }
//                            }
//                        }
//                    }
//                }
//            }

            //System.out.println(ReflectionToStringBuilder.toString(confReader,ToStringStyle.MULTI_LINE_STYLE));

        } catch (Exception e) {

            // TODO Auto-generated catch block

            e.printStackTrace();

        }


    }
}
