

package streamclients.util;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.deser.std.StdDeserializer;
import com.fasterxml.jackson.databind.node.ArrayNode;

import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;


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

        ArrayNode array = (ArrayNode)memStatNode.at("/notification/push-update/datastore-contents-xml/memory-statistics/memory-statistic");
        Map<String, Long> map = new HashMap<>();
        for (JsonNode node: array) {
            map.put(node.get("name").asText(), Long.parseLong(node.get("used-memory").asText()));
        }
        memStat.setMemoryStatistic(map);

        String eventTime = memStatNode.at("/notification/eventTime").asText();
        memStat.setEventTime(eventTime);

        return memStat;
    }
}