/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements. See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package client;

import client.model.Statistic;
import client.model.Statistics;
import client.processor.StatisticTransformer;
import client.serde.StatisticsDeserializer;
import client.serde.JsonPOJODeserializer;
import client.serde.JsonPOJOSerializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
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

/**
 * In this example, we implement a simple LineSplit program using the high-level Streams DSL
 * that reads from a source topic "streams-plaintext-input", where the values of messages represent lines of text,
 * and writes the messages as-is into a sink topic "streams-pipe-output".
 */
public class OATSStatisticsClient {

    private static final long THRESHOLD =  100000;
    private static final String INPUTTOPIC = "interfaces-out-discards";
    private static final String OUTPUTTOPIC = "out-discards-events";
    public static final String STAT_STATESTORE = "iface-stat-statestore";

    public static void main(String[] args) throws Exception {
        // read OATS-Config
        ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());


        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "iface-stats-client");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG, LogAndContinueExceptionHandler.class);

        ObjectMapper mapper = new ObjectMapper();
        SimpleModule module = new SimpleModule();
        module.addDeserializer(Statistics.class, new StatisticsDeserializer());
        mapper.registerModule(module);

        final StreamsBuilder builder = new StreamsBuilder();
        Map<String, Object> serdeProps = new HashMap<>();

        final Serializer<Statistics> ifaceStatsSerializer = new JsonPOJOSerializer<>();
        serdeProps.put("JsonPOJOClass", Statistics.class);
        ifaceStatsSerializer.configure(serdeProps, false);

        final Deserializer<Statistics> ifaceStatsDeserializer = new JsonPOJODeserializer<>();
        serdeProps.put("JsonPOJOClass", Statistics.class);
        ifaceStatsDeserializer.configure(serdeProps, false);

        final Serde<Statistics> ifaceStatsSerde = Serdes.serdeFrom(ifaceStatsSerializer, ifaceStatsDeserializer);

        final Serializer<Statistic> ifaceStatSerializer = new JsonPOJOSerializer<>();
        serdeProps.put("JsonPOJOClass", Statistic.class);
        ifaceStatSerializer.configure(serdeProps, false);

        final Deserializer<Statistic> ifaceStatDeserializer = new JsonPOJODeserializer<>();
        serdeProps.put("JsonPOJOClass", Statistic.class);
        ifaceStatDeserializer.configure(serdeProps, false);

        final Serde<Statistic> ifaceStatSerde = Serdes.serdeFrom(ifaceStatSerializer, ifaceStatDeserializer);

        StoreBuilder<KeyValueStore<String, Statistic>> ifaceStatSupplier = Stores.keyValueStoreBuilder(
                Stores.inMemoryKeyValueStore
                        (STAT_STATESTORE),
                        Serdes.String(),
                        ifaceStatSerde);
        builder.addStateStore(ifaceStatSupplier);

        KStream<String, String> raw = builder.stream(INPUTTOPIC);
        KStream<String, Statistics> statsStream = raw.map((KeyValueMapper<String, String, KeyValue<String, Statistics>>) (key, value) -> {
            Statistics stat = new Statistics();
            try {
                stat = mapper.readValue(value, Statistics.class);
            } catch (IOException ex) {
                System.out.println (ex.toString());
            }
            return new KeyValue<>(key, stat);
        });

        KStream<String, Statistic> ifaceStatStream = statsStream
                .flatMapValues(value -> value.getIfaceStatistics())
                .map((key, value) -> new KeyValue<>(key, value));

        KStream<String, Statistic> eventStream = ifaceStatStream
                .transform(() -> new StatisticTransformer(THRESHOLD), STAT_STATESTORE);


        eventStream
                .filter((key, value) -> key != null)
                .to(OUTPUTTOPIC, Produced.with(Serdes.String(), ifaceStatSerde));

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
