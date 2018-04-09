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

import client.model.InterfaceStatistic;
import client.model.InterfaceStatistics;
import client.serde.InterfaceStatisticsDeserializer;
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

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;

/**
 * In this example, we implement a simple LineSplit program using the high-level Streams DSL
 * that reads from a source topic "streams-plaintext-input", where the values of messages represent lines of text,
 * and writes the messages as-is into a sink topic "streams-pipe-output".
 */
public class InterfaceStatisticsClient {

    public static void main(String[] args) throws Exception {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "iface-stats-client");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG, LogAndContinueExceptionHandler.class);

        ObjectMapper mapper = new ObjectMapper();
        SimpleModule module = new SimpleModule();
        module.addDeserializer(InterfaceStatistics.class, new InterfaceStatisticsDeserializer());
        mapper.registerModule(module);

        final StreamsBuilder builder = new StreamsBuilder();
        Map<String, Object> serdeProps = new HashMap<>();

        final Serializer<InterfaceStatistics> ifaceStatsSerializer = new JsonPOJOSerializer<>();
        serdeProps.put("JsonPOJOClass", InterfaceStatistics.class);
        ifaceStatsSerializer.configure(serdeProps, false);

        final Deserializer<InterfaceStatistics> ifaceStatsDeserializer = new JsonPOJODeserializer<>();
        serdeProps.put("JsonPOJOClass", InterfaceStatistics.class);
        ifaceStatsDeserializer.configure(serdeProps, false);

        final Serde<InterfaceStatistics> ifaceStatsSerde = Serdes.serdeFrom(ifaceStatsSerializer, ifaceStatsDeserializer);

        final Serializer<InterfaceStatistic> ifaceStatSerializer = new JsonPOJOSerializer<>();
        serdeProps.put("JsonPOJOClass", InterfaceStatistic.class);
        ifaceStatSerializer.configure(serdeProps, false);

        final Deserializer<InterfaceStatistic> ifaceStatDeserializer = new JsonPOJODeserializer<>();
        serdeProps.put("JsonPOJOClass", InterfaceStatistic.class);
        ifaceStatDeserializer.configure(serdeProps, false);

        final Serde<InterfaceStatistic> ifaceStatSerde = Serdes.serdeFrom(ifaceStatSerializer, ifaceStatDeserializer);



        KStream<String, String> raw = builder.stream("interfaces-out-discards");
        KStream<String, InterfaceStatistics> statsStream = raw.map((KeyValueMapper<String, String, KeyValue<String, InterfaceStatistics>>) (key, value) -> {
            InterfaceStatistics stat = new InterfaceStatistics();
            try {
                stat = mapper.readValue(value, InterfaceStatistics.class);
            } catch (IOException ex) {
                System.out.println (ex.toString());
            }
            return new KeyValue<>(key, stat);
        });
        Map<String, InterfaceStatistic> statsMap = new HashMap<>();
        KStream<String, List<InterfaceStatistic>> ifaceStatStream = statsStream
                .map((key, value) -> new KeyValue<>(key, value.getIfaceStatistics()));

        KStream<String, InterfaceStatistic> nonZeroStream = statsStream.flatMapValues(value -> value.getIfaceStatistics())
                .filter(InterfaceStatistic::filterNonZero)
                .map((key, value) -> new KeyValue<>(key, value));

        //Map<String, InterfaceStatistic> finalStatsMap = statsMap;
        //ifaceStatStream.foreach((key, value) -> finalStatsMap.put(key, value));
        //eventStream.to( "streams-pipe-output", Produced.with(Serdes.String(), ifaceStatSerde));
        nonZeroStream.to( "streams-pipe-output", Produced.with(Serdes.String(), ifaceStatSerde));

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
