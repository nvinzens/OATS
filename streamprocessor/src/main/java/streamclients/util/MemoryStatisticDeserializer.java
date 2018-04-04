

package streamclients.util;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.deser.std.StdDeserializer;

import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

@JsonDeserialize(using = MemoryStatisticDeserializer.class)
public class MemoryStatisticDeserializer extends StdDeserializer<MemoryStatistic> {

    public MemoryStatisticDeserializer() {
        this(null);
    }

    public MemoryStatisticDeserializer(Class<?> vc) {
        super(vc);
    }

    @Override
    public MemoryStatistic deserialize(JsonParser jp, DeserializationContext ctxt)
            throws IOException, JsonProcessingException {

        JsonNode memStatNode = jp.getCodec().readTree(jp);
        MemoryStatistic memStat = new MemoryStatistic();
        memStat.setEventTime(getEventTime(memStatNode));
        Map<String, String> memoryStats = new HashMap<>();
        memoryStats = getMemoryStatistics(memStatNode, memoryStats);
        memStat.setMemoryStatistic(memoryStats);

        return memStat;
    }

    private static void getFields(JsonNode node) {
        Iterator<String> fieldNames = node.fieldNames();
        while (fieldNames.hasNext()) {
            String fieldName = fieldNames.next();
            JsonNode fieldValue = node.get(fieldName);
            if (fieldValue.isObject()) {
                //System.out.println(fieldName + " :");
                getFields(fieldValue);
            } else if (fieldValue.isArray()) {
                String value = fieldValue.asText();
                Iterator<JsonNode> it = fieldValue.elements();
                while (it.hasNext()) {
                    JsonNode n = it.next();
                    System.out.println(n.get("name"));
                    System.out.println(n.get("used-memory"));
                }
            } else {
                String value = fieldValue.asText();
                if (fieldName == "eventTime") {
                    System.out.println(fieldName + " : " + value);
                }
            }
        }
    }

    private String getEventTime(JsonNode node) {
        Iterator<String> fieldNames = node.fieldNames();
        while (fieldNames.hasNext()) {
            String fieldName = fieldNames.next();
            JsonNode fieldValue = node.get(fieldName);
            if (fieldValue.isObject()) {
                getEventTime(fieldValue);
            } else {
                String value = fieldValue.asText();
                if (fieldName == "eventTime") {
                    return value;
                }
                return "";
            }
        }
        return "";
    }

    private Map<String, String> getMemoryStatistics(JsonNode node, Map<String, String> map) {
        Iterator<String> fieldNames = node.fieldNames();
        while (fieldNames.hasNext()) {
            String fieldName = fieldNames.next();
            JsonNode fieldValue = node.get(fieldName);
            if (fieldValue.isObject()) {
                getMemoryStatistics(fieldValue, map);
            } else if (fieldValue.isArray()) {
                Iterator<JsonNode> it = fieldValue.elements();
                while (it.hasNext()) {
                    JsonNode n = it.next();
                    map.put(n.get("name").asText(), n.get("used-memory").asText());
                }
                return map;
            } else {
                return null;
            }
        }
        return map;
    }

}