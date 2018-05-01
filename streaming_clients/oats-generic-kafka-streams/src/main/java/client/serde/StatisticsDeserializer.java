package client.serde;

import client.model.Statistic;
import client.model.Statistics;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.deser.std.StdDeserializer;
import com.fasterxml.jackson.databind.node.ArrayNode;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class StatisticsDeserializer extends StdDeserializer<Statistics>  {

    public StatisticsDeserializer() { this(null); }

    public StatisticsDeserializer(Class<?> vc) {
        super(vc);
    }

    @Override
    public Statistics deserialize(JsonParser jsonParser, DeserializationContext deserializationContext) throws IOException, JsonProcessingException {
        JsonNode ifaceNode = jsonParser.getCodec().readTree(jsonParser);
        Statistics stats = new Statistics();

        //String et = ifaceNode.at("/notification/eventTime").asText();
        //stats.setEventTime(et);

        ArrayNode array = (ArrayNode)ifaceNode.at("/notification/push-update/datastore-contents-xml/interfaces-state/interface");
        List<Statistic> list = new ArrayList<>();
        for (JsonNode node : array) {
            Statistic stat = new Statistic();
            stat.setIfaceName(node.get("name").asText());
            //stat.setOutDiscards(node.at("/statistics/out-discards").asLong());
            list.add(stat);
        }
        stats.setIfaceStatistics(list);

        return stats;
    }
}
