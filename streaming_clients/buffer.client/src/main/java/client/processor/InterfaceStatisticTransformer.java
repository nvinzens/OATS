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

    private long threshhold;

    public InterfaceStatisticTransformer(long threshhold) {
        this.threshhold = threshhold;
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
            //System.out.println("oldstat zero");
            oldStat = new InterfaceStatistic();
            oldStat.setIfaceName(newStat.getIfaceName());
            oldStat.setOutDiscards(0);
        }
        if ((newStat.getOutDiscards() - oldStat.getOutDiscards()) > threshhold) {
            System.out.println(newStat.getIfaceName());
            System.out.println(newStat.getOutDiscards());
            System.out.println(oldStat.getIfaceName());
            System.out.println(oldStat.getOutDiscards());
            statStore.put(key+newStat.getIfaceName(), newStat);
            return new KeyValue<>(key, newStat);
        }
        //System.out.println(key);
        //System.out.println(statStore.get(key+newStat.getIfaceName()).getIfaceName());
        //System.out.println(statStore.get(key+newStat.getIfaceName()).getOutDiscards());
        statStore.put(key+newStat.getIfaceName(), newStat);
        return new KeyValue<>(null, null);
    }
}
