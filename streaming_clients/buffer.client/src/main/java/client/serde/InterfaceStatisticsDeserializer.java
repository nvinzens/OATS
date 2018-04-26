package client.serde;

import client.model.InterfaceStatistic;
import client.model.InterfaceStatistics;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.deser.std.StdDeserializer;
import com.fasterxml.jackson.databind.node.ArrayNode;
import javafx.util.Pair;

import java.io.IOException;
import java.util.*;

public class InterfaceStatisticsDeserializer extends StdDeserializer<InterfaceStatistics>  {

    public InterfaceStatisticsDeserializer() { this(null); }

    public InterfaceStatisticsDeserializer(Class<?> vc) {
        super(vc);
    }

    @Override
    public InterfaceStatistics deserialize(JsonParser jsonParser, DeserializationContext deserializationContext) throws IOException, JsonProcessingException {
        JsonNode ifaceNode = jsonParser.getCodec().readTree(jsonParser);
        InterfaceStatistics stats = new InterfaceStatistics();

        String et = ifaceNode.at("/notification/eventTime").asText();
        stats.setEventTime(et);

        ArrayNode array = (ArrayNode)ifaceNode.at("/notification/push-update/datastore-contents-xml/interfaces-state/interface");
        List<InterfaceStatistic> list = new ArrayList<>();
        for (JsonNode node : array) {
            InterfaceStatistic stat = new InterfaceStatistic();
            stat.setIfaceName(node.get("name").asText());
            stat.setOutDiscards(node.at("/statistics/out-discards").asLong());
            list.add(stat);
        }
        stats.setIfaceStatistics(list);

        return stats;
    }
}
