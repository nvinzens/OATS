package client.serde;

import client.OATSStatisticsClient;
import client.model.OATSArgs;
import client.model.Statistic;
import client.model.Statistics;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.deser.std.StdDeserializer;
import com.fasterxml.jackson.databind.node.ArrayNode;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class StatisticsDeserializer extends StdDeserializer<Statistics>  {

    private OATSArgs args;

    public StatisticsDeserializer(OATSArgs args) {
        this(Statistics.class);
        this.args = args;
    }

    protected StatisticsDeserializer(Class<?> vc) {
        super(vc);
    }

    /**
     * Takes data from the input topic and deserializes it into an object of the Statistics class.
     */
    @Override
    public Statistics deserialize(JsonParser jsonParser, DeserializationContext deserializationContext) throws IOException {
        JsonNode statNode = jsonParser.getCodec().readTree(jsonParser);
        Statistics stats = new Statistics();

        String et = statNode.at("/notification/eventTime").asText();
        stats.setEventTime(et);
        ArrayNode array = (ArrayNode)statNode.at(args.getRootXpath());
        List<Statistic> list = new ArrayList<>();
        for (JsonNode node : array) {
            Statistic stat = new Statistic();
            stat.setName(node.at(args.getNameXpath()).asText());
            stat.setValue(node.at(args.getDataXpath()).asLong());
            list.add(stat);
        }
        stats.setStatistics(list);

        return stats;
    }
}
