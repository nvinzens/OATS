package tests;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.jayway.jsonpath.JsonPath;
import streamclients.util.MemoryStatistic;
import streamclients.util.MemoryStatisticDeserializer;

import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

public class JsonTest {

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        String json = "{\"notification\": " +
                "{\"@xmlns\": \"urn:ietf:params:xml:ns:netconf:notification:1.0\", " +
                "\"eventTime\": \"2018-04-03T00:12:46.28Z\", " +
                "\"push-update\": " +
                "{\"@xmlns\": \"urn:ietf:params:xml:ns:yang:ietf-yang-push\", " +
                "\"subscription-id\": \"2147483881\", " +
                "\"datastore-contents-xml\": {" +
                "\"memory-statistics\": {" +
                "\"@xmlns\": \"http://cisco.com/ns/yang/Cisco-IOS-XE-memory-oper\", " +
                "\"memory-statistic\": [" +
                "{\"name\": \"Processor\", \"used-memory\": \"314265100\"}, {\"name\": \"lsmpi_io\", \"used-memory\": \"6294304\"}" +
                "]" +
                "}}}}}";

        JsonNode root = mapper.readTree(json);

        JsonNode not = root.path("notification");

        /**
        Iterator<String> fieldNames = root.fieldNames();
        MemoryStatistic memStat = new MemoryStatistic();

        ArrayNode array = (ArrayNode)root.at("/notification/push-update/datastore-contents-xml/memory-statistics/memory-statistic");
        Map<String, Long> map = new HashMap<>();
        for (JsonNode node: array) {
            map.put(node.get("name").asText(), Long.parseLong(node.get("used-memory").asText()));
            System.out.println(node.get("name").asText());
            System.out.println(Long.parseLong(node.get("used-memory").asText()));
        }
        memStat.setMemoryStatistic(map);

        String eventTime = root.at("/notification/eventTime").asText();
        System.out.println(eventTime);
        memStat.setEventTime(eventTime);
        System.out.println(memStat.toString());
        //String name = root.get("notification").textValue();
        List<String> h = JsonPath.parse(json).read("$.notification.push-update.datastore-contents-xml.memory-statistics.memory-statistic[*].name");
        for (String name: h) {
            System.out.println(name);
        }
         **/

        //System.out.println(name);
        //System.out.println(not.textValue());
        //printAll(root);
        SimpleModule module = new SimpleModule();
        module.addDeserializer(MemoryStatistic.class, new MemoryStatisticDeserializer());
        mapper.registerModule(module);
        MemoryStatistic stat = mapper.readValue(json, MemoryStatistic.class);

        System.out.println(stat.toString());

        //System.out.println(mapper.readValue(json, MemoryStatistic.class));

        //System.out.println("blabla" + root.get("eventTime").textValue());

        //String string = root.get("datastore-contents-xml")
         //       .get("memory-statistics").get("memory-statistic").get(0).textValue();



    }
/**
    @JsonIgnoreProperties(ignoreUnknown = true)
    private static class MemoryStatistic {

        private long eventTime;

        @JsonProperty("memory-statistic")
        private List<String> memoryStatistic;

        public void setEventTime(long eventTime) {
            this.eventTime = eventTime;
        }

        public long getEventTime() {
            return eventTime;
        }

        public void setMemoryStatistic(List<String> memoryStatistic) {
            this.memoryStatistic = memoryStatistic;
        }

        public List<String> getMemoryStatistic() {
            return memoryStatistic;
        }

        @Override
        public String toString() {
            return "EventTime: " + eventTime + ", MemoryStatistic: " + memoryStatistic;
        }

        @JsonProperty("datastore-contents-xml")
        private void unpackNested(Map<String,Object> datastore) {
            String memoryStats = (String)datastore.get("memory-statistics");
            System.out.println(memoryStats);

            List<Map<String,String>> owner = (Map<String,String>)memoryStats.get("memory-statistics");
            String processName = owner.get(0).get("name");
            System.out.println(processName);
        }


    }
        **/

    public static void printAll(JsonNode node) {
        Iterator<String> fieldNames = node.fieldNames();
        while(fieldNames.hasNext()){
            String fieldName = fieldNames.next();
            JsonNode fieldValue = node.get(fieldName);
            if (fieldValue.isObject()) {
                System.out.println(fieldName + " :");
                printAll(fieldValue);
            } else if (fieldValue.isArray()) {
                String value = fieldValue.asText();
                Iterator<JsonNode> it = fieldValue.elements();
                while (it.hasNext()) {
                    JsonNode n = it.next();
                    System.out.println(n.get("name"));
                    System.out.println(n.get("used-memory"));
                }
            }
            else {
                String value = fieldValue.asText();
                if (fieldName == "eventTime") {
                    System.out.println(fieldName + " : " + value);
                }
            }
        }
    }


}