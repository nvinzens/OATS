package client.processor;

import client.InterfaceStatisticsClient;
import client.model.InterfaceStatistic;
import client.model.InterfaceStatistics;
import org.apache.kafka.streams.processor.Processor;
import org.apache.kafka.streams.processor.ProcessorContext;
import org.apache.kafka.streams.state.KeyValueStore;

import java.util.ArrayList;
import java.util.List;

public class InterfaceStatisticsProcessor implements Processor<String, InterfaceStatistics> {

    private ProcessorContext context;
    private long threshhold;


    public InterfaceStatisticsProcessor(long threshhold) {
        this.threshhold = threshhold;
    }

    @Override
    public void init(ProcessorContext processorContext) {
        this.context = processorContext;

    }

    @Override
    public void process(String key, InterfaceStatistics interfaceStatistics) {
        context.forward(key, interfaceStatistics);
    }


    @Override
    public void punctuate(long l) { }

    @Override
    public void close() { }


}
