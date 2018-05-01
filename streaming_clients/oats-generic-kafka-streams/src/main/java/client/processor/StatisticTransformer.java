package client.processor;

import client.OATSStatisticsClient;
import client.model.Statistic;
import org.apache.kafka.streams.KeyValue;
import org.apache.kafka.streams.kstream.Transformer;
import org.apache.kafka.streams.processor.ProcessorContext;
import org.apache.kafka.streams.state.KeyValueStore;

public class StatisticTransformer implements Transformer<String, Statistic, KeyValue<String, Statistic>> {

    private ProcessorContext context;
    private KeyValueStore<String, Statistic> statStore;

    private long threshold;

    public StatisticTransformer(long threshold) {
        this.threshold = threshold;
    }

    @Override
    public void init(ProcessorContext processorContext) {
        this.context = processorContext;
        statStore = (KeyValueStore) context.getStateStore(OATSStatisticsClient.STAT_STATESTORE);
    }

    @SuppressWarnings("deprecation")
    @Override
    public KeyValue<String, Statistic> punctuate(long l) { return null; }

    @Override
    public void close() { }

    @Override
    public KeyValue<String, Statistic> transform(String key, Statistic newStat) {
        Statistic oldStat = statStore.get(key+newStat.getIfaceName());
        if (oldStat == null) {
            oldStat = new Statistic();
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
