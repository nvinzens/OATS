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
package streamclients;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.Deserializer;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.Serializer;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.errors.LogAndContinueExceptionHandler;
import org.apache.kafka.streams.errors.ProductionExceptionHandler;
import org.apache.kafka.streams.errors.ProductionExceptionHandler.ProductionExceptionHandlerResponse;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.KeyValueMapper;
import org.apache.kafka.streams.kstream.Produced;
import streamclients.util.JsonPOJODeserializer;
import streamclients.util.JsonPOJOSerializer;

import streamclients.util.MemoryStatistic;
import streamclients.util.MemoryStatisticDeserializer;

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
public class Pipe {


    public static void main(String[] args) throws Exception {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "streams-pipe");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
        props.put(StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG, LogAndContinueExceptionHandler.class);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        ObjectMapper mapper = new ObjectMapper();
        SimpleModule module = new SimpleModule();
        module.addDeserializer(MemoryStatistic.class, new MemoryStatisticDeserializer());
        mapper.registerModule(module);

        final StreamsBuilder builder = new StreamsBuilder();
        Map<String, Object> serdeProps = new HashMap<>();

        final Serializer<MemoryStatistic> memStatSerializer = new JsonPOJOSerializer<>();
        serdeProps.put("JsonPOJOClass", MemoryStatistic.class);
        memStatSerializer.configure(serdeProps, false);

        final Deserializer<MemoryStatistic> memStatDeserializer = new JsonPOJODeserializer<>();
        serdeProps.put("JsonPOJOClass", MemoryStatistic.class);
        memStatDeserializer.configure(serdeProps, false);

        final Serde<MemoryStatistic> memStatSerde = Serdes.serdeFrom(memStatSerializer, memStatDeserializer);


        KStream<String, String> raw = builder.stream("oats");
        KStream<String, MemoryStatistic> memStream = raw.map((KeyValueMapper<String, String, KeyValue<String, MemoryStatistic>>) (key, value) -> {
            MemoryStatistic stat = new MemoryStatistic();
            try {
                stat = mapper.readValue(value, MemoryStatistic.class);
            } catch (IOException ex) {
                System.out.println (ex.toString());
            }
            return new KeyValue<>(key, stat);
        });
        memStream.through("streams-pipe-output", Produced.with(Serdes.String(), memStatSerde))
            .filter((key, value) -> key.equals("10.20.1.21"))
            .to("host-test", Produced.with(Serdes.String(), memStatSerde));

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
