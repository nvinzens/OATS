package tests;

import client.model.InterfaceStatistic;
import client.model.InterfaceStatistics;

import client.serde.InterfaceStatisticsDeserializer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.databind.node.ArrayNode;
import javafx.util.Pair;

import javax.xml.crypto.dsig.keyinfo.KeyValue;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

public class Test {


    public static void main(String[] args) throws Exception {
        String eventTime = "2018-04-03T00:12:46.28Z";
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS");
        //LocalDate parsedDate = LocalDate.parse(eventTime, formatter);
        //System.out.println(parsedDate.toString());

        Instant instant = Instant.parse("2018-04-03T00:12:46.28Z");
        //System.out.println(instant);
        Timestamp ts = Timestamp.from(instant);
        //System.out.println(ts);

        ObjectMapper mapper = new ObjectMapper();
        SimpleModule module = new SimpleModule();

        String json = "{\"notification\": {" +
                "\"@xmlns\": " +
                "\"urn:ietf:params:xml:ns:netconf:notification:1.0\", " +
                "\"eventTime\": \"2018-04-07T21:45:38.20Z\", " +
                "\"push-update\": {" +
                "\"@xmlns\": \"urn:ietf:params:xml:ns:yang:ietf-yang-push\", " +
                "\"subscription-id\": \"2147483661\", " +
                "\"datastore-contents-xml\": {" +
                "\"interfaces-state\": {" +
                "\"@xmlns\": \"urn:ietf:params:xml:ns:yang:ietf-interfaces\", " +
                "\"interface\": [{" +
                    "\"name\": \"GigabitEthernet0/0\", " +
                    "\"statistics\": {\"out-discards\": \"5\"}}, " +
                "{\"name\": \"GigabitEthernet1/0/1\", \"statistics\": {\"out-discards\": \"10\"}}, {\"name\": \"GigabitEthernet1/0/10\", \"statistics\": {\"out-discards\": \"13\"}}, {\"name\": \"GigabitEthernet1/0/11\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/12\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/13\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/14\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/15\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/16\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/17\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/18\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/19\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/2\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/20\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/21\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/22\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/23\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/24\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/3\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/4\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/5\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/6\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/7\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/8\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/0/9\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/1/1\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/1/2\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/1/3\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"GigabitEthernet1/1/4\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"TenGigabitEthernet1/1/1\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"TenGigabitEthernet1/1/2\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"TenGigabitEthernet1/1/3\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"TenGigabitEthernet1/1/4\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"Vlan1\", \"statistics\": {\"out-discards\": \"0\"}}, {\"name\": \"Vlan666\", \"statistics\": {\"out-discards\": \"0\"}}]}}}}}";
        JsonNode ifaceStatsNode = mapper.readTree(json);
        InterfaceStatistics stats = new InterfaceStatistics();
        String et = ifaceStatsNode.at("/notification/eventTime").asText();
        stats.setEventTime(et);

        ArrayNode array = (ArrayNode)ifaceStatsNode.at("/notification/push-update/datastore-contents-xml/interfaces-state/" +
                "interface");
        List<InterfaceStatistic> list = new ArrayList<>();
        for (JsonNode node : array) {
            InterfaceStatistic stat = new InterfaceStatistic();
            stat.setIfaceName(node.get("name").asText());
            stat.setOutDiscards(node.at("/statistics/out-discards").asLong());
            list.add(stat);
            }
        stats.setIfaceStatistics(list);
        for (InterfaceStatistic stat : stats.getIfaceStatistics()) {
            System.out.println(stat.getIfaceName());
            System.out.println(stat.getOutDiscards());
        }


        /**
        module.addDeserializer(InterfaceStatistics.class, new InterfaceStatisticsDeserializer());
        mapper.registerModule(module);
        stats = mapper.readValue(json, InterfaceStatistics.class);
        System.out.println(stats.getEventTime());
        for (Map.Entry<String, Pair<String, Long>> entry : map.entrySet()) {
            System.out.println(entry.getKey());
            System.out.println(entry.getValue().getKey());
            System.out.println(entry.getValue().getValue());
        }
         **/






    }
}
