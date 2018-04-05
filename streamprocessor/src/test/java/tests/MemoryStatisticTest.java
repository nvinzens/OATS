package tests;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import org.junit.Before;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import streamclients.util.MemoryStatistic;
import streamclients.util.MemoryStatisticDeserializer;

import java.io.IOException;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class MemoryStatisticTest {

    private String jsonString = "{\"notification\": " +
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
    private ObjectMapper mapper = new ObjectMapper();
    private SimpleModule module = new SimpleModule();
    private MemoryStatistic stat;

    @Test
    public void testEventTimeDeSerialization() throws IOException {
        this.module.addDeserializer(MemoryStatistic.class, new MemoryStatisticDeserializer());
        this.mapper.registerModule(this.module);
        stat = mapper.readValue(jsonString, MemoryStatistic.class);
        String eventTime = "2018-04-03T00:12:46.28Z";
        assertEquals(eventTime, stat.getEventTime());
    }

    @Test
    public void testMemoryStatisticDeserializarion() throws IOException {
        this.module.addDeserializer(MemoryStatistic.class, new MemoryStatisticDeserializer());
        this.mapper.registerModule(this.module);
        stat = mapper.readValue(jsonString, MemoryStatistic.class);
        String firstProcess = "Processor";
        String secondProcess = "lsmpi_io";
        long firstUsedMemory = 314265100;
        long secondUsedMemory = 6294304;
        Map<String, Long> memStatMap = stat.getMemoryStatistic();
        assertEquals(firstUsedMemory, memStatMap.get(firstProcess).longValue());
        assertEquals(secondUsedMemory, memStatMap.get(secondProcess).longValue());
    }

}
