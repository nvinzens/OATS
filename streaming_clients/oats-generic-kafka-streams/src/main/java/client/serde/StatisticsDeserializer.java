package client.serde;

import client.model.OATSArgs;
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
        JsonNode statNode = jsonParser.getCodec().readTree(jsonParser);
        Statistics stats = new Statistics();

        String et = statNode.at("/notification/eventTime").asText();
        stats.setEventTime(et);

        ArrayNode array = (ArrayNode)statNode.at(OATSArgs.rootXpath);
        List<Statistic> list = new ArrayList<>();
        for (JsonNode node : array) {
            Statistic stat = new Statistic();
            stat.setName(node.get(OATSArgs.nameXpath).asText());
            stat.setValue(node.at(OATSArgs.dataXpath).asLong());
            list.add(stat);
        }
        stats.setStatistics(list);

        return stats;
    }
}
