package client;

import client.model.OATSArgs;
import client.model.Statistic;
import client.model.Statistics;
import client.processor.StatisticTransformer;
import client.serde.StatisticsDeserializer;
import client.serde.JsonPOJODeserializer;
import client.serde.JsonPOJOSerializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import org.apache.kafka.common.serialization.Deserializer;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.Serializer;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.errors.LogAndContinueExceptionHandler;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.KeyValueMapper;
import org.apache.kafka.streams.kstream.Produced;
import org.apache.kafka.streams.state.KeyValueStore;
import org.apache.kafka.streams.state.StoreBuilder;
import org.apache.kafka.streams.state.Stores;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;


public class OATSStatisticsClient {


    public static void main(String[] args) throws Exception {

        OATSArgs arguments = new OATSArgs(args);

        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, arguments.getInputTopic() + "-client");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG, LogAndContinueExceptionHandler.class);

        ObjectMapper mapper = new ObjectMapper();
        SimpleModule module = new SimpleModule();
        module.addDeserializer(Statistics.class, new StatisticsDeserializer(arguments));
        mapper.registerModule(module);

        final StreamsBuilder builder = new StreamsBuilder();
        Map<String, Object> serdeProps = new HashMap<>();


        final Serializer<Statistic> StatSerializer = new JsonPOJOSerializer<>();
        serdeProps.put("JsonPOJOClass", Statistic.class);
        StatSerializer.configure(serdeProps, false);

        final Deserializer<Statistic> StatDeserializer = new JsonPOJODeserializer<>();
        serdeProps.put("JsonPOJOClass", Statistic.class);
        StatDeserializer.configure(serdeProps, false);

        final Serde<Statistic> StatSerde = Serdes.serdeFrom(StatSerializer, StatDeserializer);

        StoreBuilder<KeyValueStore<String, Statistic>> StatSupplier = Stores.keyValueStoreBuilder(
                Stores.inMemoryKeyValueStore
                        (arguments.getStatStateStore()),
                        Serdes.String(),
                        StatSerde);
        builder.addStateStore(StatSupplier);

        KStream<String, String> raw = builder.stream(arguments.getInputTopic());
        KStream<String, Statistics> statsStream = raw.map((KeyValueMapper<String, String, KeyValue<String, Statistics>>) (key, value) -> {
            Statistics stat = new Statistics();
            try {
                stat = mapper.readValue(value, Statistics.class);
            } catch (IOException ex) {
                System.out.println (ex.toString());
            }
            return new KeyValue<>(key, stat);
        });

        KStream<String, Statistic> StatStream = statsStream
                .flatMapValues(Statistics::getStatistics)
                .map(KeyValue::new);

        KStream<String, Statistic> eventStream = StatStream
                .transform(() -> new StatisticTransformer(arguments), arguments.getStatStateStore());


        eventStream
                .filter((key, value) -> key != null)
                .to(arguments.getOutputTopic(), Produced.with(Serdes.String(), StatSerde));

        final Topology topology = builder.build();
        final KafkaStreams streams = new KafkaStreams(topology, props);
        final CountDownLatch latch = new CountDownLatch(1);

        // attach shutdown handler to catch control-c
        Runtime.getRuntime().addShutdownHook(new Thread("streams-shutdown-hook") {
            @Override
            public void run() {
                streams.close();
                latch.countDown();
            }
        });

        try {
            streams.start();
            latch.await();
        } catch (Throwable e) {
            System.exit(1);
        }
        System.exit(0);
    }
}
