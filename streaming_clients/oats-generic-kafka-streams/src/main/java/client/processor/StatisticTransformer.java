package client.processor;

import client.model.OATSArgs;
import client.model.Statistic;
import org.apache.kafka.streams.KeyValue;
import org.apache.kafka.streams.kstream.Transformer;
import org.apache.kafka.streams.processor.ProcessorContext;
import org.apache.kafka.streams.state.KeyValueStore;

public class StatisticTransformer implements Transformer<String, Statistic, KeyValue<String, Statistic>> {

    private ProcessorContext context;
    private KeyValueStore<String, Statistic> statStore;

    private OATSArgs args;

    public StatisticTransformer(OATSArgs args) {
        this.args = args;
    }

    @Override
    public void init(ProcessorContext processorContext) {
        this.context = processorContext;
        statStore = (KeyValueStore) context.getStateStore(args.getStatStateStore());
    }

    @SuppressWarnings("deprecation")
    @Override
    public KeyValue<String, Statistic> punctuate(long l) { return null; }

    @Override
    public void close() { }

    @Override
    public KeyValue<String, Statistic> transform(String key, Statistic newStat) {
        Statistic oldStat = statStore.get(key+newStat.getName());
        if (oldStat == null) {
            oldStat = new Statistic();
            oldStat.setName(newStat.getName());
            oldStat.setValue(0);
        }
        switch(args.getOperator()) {
            case EQUALS:
                if ((newStat.getValue() - oldStat.getValue()) == args.getThreshold()) {
                    statStore.put(key+newStat.getName(), newStat);
                    return new KeyValue<>(key, newStat);
                }
            case GREATER_THAN:
                if ((newStat.getValue() - oldStat.getValue()) > args.getThreshold()) {
                    statStore.put(key + newStat.getName(), newStat);
                    return new KeyValue<>(key, newStat);
                }
            case SMALLER_THAN:
                if ((newStat.getValue() - oldStat.getValue()) < args.getThreshold()) {
                    statStore.put(key+newStat.getName(), newStat);
                    return new KeyValue<>(key, newStat);
                }
            case GREATER_OR_EQUAL:
                if ((newStat.getValue() - oldStat.getValue()) >= args.getThreshold()) {
                    statStore.put(key+newStat.getName(), newStat);
                    return new KeyValue<>(key, newStat);
                }
            case SMALLER_OR_EQUAL:
                if ((newStat.getValue() - oldStat.getValue()) <= args.getThreshold()) {
                    statStore.put(key+newStat.getName(), newStat);
                    return new KeyValue<>(key, newStat);
                }
        }
        statStore.put(key+newStat.getName(), newStat);
        return new KeyValue<>(null, null);
    }
}