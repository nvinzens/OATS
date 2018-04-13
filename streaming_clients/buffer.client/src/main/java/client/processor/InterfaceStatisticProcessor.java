package client.processor;

import client.InterfaceStatisticsClient;
import client.model.InterfaceStatistic;
import org.apache.kafka.streams.processor.Processor;
import org.apache.kafka.streams.processor.ProcessorContext;
import org.apache.kafka.streams.state.KeyValueStore;

public class InterfaceStatisticProcessor implements Processor<String, InterfaceStatistic> {

    private ProcessorContext context;
    private KeyValueStore<String, InterfaceStatistic> statStore;

    private long threshhold;

    public InterfaceStatisticProcessor(long threshhold) {
        this.threshhold = threshhold;
    }


    @Override
    public void init(ProcessorContext processorContext) {
        this.context = processorContext;
        statStore = (KeyValueStore) context.getStateStore(InterfaceStatisticsClient.STAT_STATESTORE);
    }

    @Override
    public void process(String key, InterfaceStatistic newStat) {

    }

    @SuppressWarnings("deprecation")
    @Override
    public void punctuate(long l) {

    }

    @Override
    public void close() {

    }
}
