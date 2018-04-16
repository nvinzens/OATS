package client.processor;

import client.InterfaceStatisticsClient;
import client.model.InterfaceStatistic;
import org.apache.kafka.streams.KeyValue;
import org.apache.kafka.streams.kstream.Transformer;
import org.apache.kafka.streams.processor.ProcessorContext;
import org.apache.kafka.streams.state.KeyValueStore;

public class InterfaceStatisticTransformer implements Transformer<String, InterfaceStatistic, KeyValue<String, InterfaceStatistic>> {

    private ProcessorContext context;
    private KeyValueStore<String, InterfaceStatistic> statStore;

    private long threshold;

    public InterfaceStatisticTransformer(long threshold) {
        this.threshold = threshold;
    }

    @Override
    public void init(ProcessorContext processorContext) {
        this.context = processorContext;
        statStore = (KeyValueStore) context.getStateStore(InterfaceStatisticsClient.STAT_STATESTORE);
    }

    @SuppressWarnings("deprecation")
    @Override
    public KeyValue<String, InterfaceStatistic> punctuate(long l) { return null; }

    @Override
    public void close() { }

    @Override
    public KeyValue<String, InterfaceStatistic> transform(String key, InterfaceStatistic newStat) {
        InterfaceStatistic oldStat = statStore.get(key+newStat.getIfaceName());
        if (oldStat == null) {
            oldStat = new InterfaceStatistic();
            oldStat.setIfaceName(newStat.getIfaceName());
            oldStat.setOutDiscards(0);
        }
        if ((newStat.getOutDiscards() - oldStat.getOutDiscards()) > threshold) {
            statStore.put(key+newStat.getIfaceName(), newStat);
            return new KeyValue<>(key, newStat);
        }
        statStore.put(key+newStat.getIfaceName(), newStat);
        return new KeyValue<>(null, null);
    }
}
