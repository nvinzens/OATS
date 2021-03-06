package tests;

import client.model.OATSArgs;
import client.model.Statistic;
import client.model.Statistics;
import client.serde.StatisticsDeserializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;

import java.io.IOException;
import java.time.Instant;
import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.Assert.assertEquals;


public class StatisticsTest {

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

    private ObjectMapper mapper;
    private SimpleModule module;
    private Statistics stat;
    OATSArgs arguments;

    @BeforeEach
    public void setup() throws IOException {
        mapper = new ObjectMapper();
        module = new SimpleModule();

        String[] args = new String[7];
        args[0] = "interfaces-out-discards";
        args[1] = "out-discards-events";
        args[2] = "100000";
        args[3] = "greater_than";
        args[4] = "/notification/push-update/datastore-contents-xml/interfaces-state/interface";
        args[5] = "/name";
        args[6] = "/statistics/out-discards";
        arguments = new OATSArgs(args);

        this.module.addDeserializer(Statistics.class, new StatisticsDeserializer(arguments));
        this.mapper.registerModule(this.module);
        stat = mapper.readValue(json, Statistics.class);
    }

    @Test
    public void testEventTimeDeSerialization() throws IOException {
        Instant eventTime = Instant.parse("2018-04-07T21:45:38.20Z");
        assertEquals(eventTime, stat.getEventTime());
    }

    @Test
    public void testStatisticsDeserializarion() throws IOException {
        String firstInterface = "GigabitEthernet0/0";
        long firstOutDiscards = 5;
        String secondInterface = "GigabitEthernet1/0/1";
        long secondOutDiscards = 10;
        List<Statistic> list = stat.getStatistics();
        assertEquals(firstInterface, list.get(0).getName());
        assertEquals(firstOutDiscards, list.get(0).getValue());
        assertEquals(secondInterface, list.get(1).getName());
        assertEquals(secondOutDiscards, list.get(1).getValue());
    }

}
