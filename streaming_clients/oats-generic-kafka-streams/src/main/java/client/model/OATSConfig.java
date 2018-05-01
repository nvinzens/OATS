package client.model;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class OATSConfig {

    private String kafkaTopic;
    private boolean evaluate;
    private long threshold;
    private Operator operator;
    private String event;
    private List<String> xpaths = new ArrayList<>();

    public OATSConfig(OATSConfigReader confReader) {
        for (Map<String, Object> map : confReader.getSubscriptions()) {
            Map<String, Object> subscription = (Map) map.get("subscription");
            for (Map.Entry<String, Object> entry : subscription.entrySet()) {
                if (entry.getKey().equals("kafka_streams_eval")) {
                    evaluate = (Boolean) entry.getValue();
                }
                if (entry.getKey().equals("event_threshold")) {
                    List<Map<String, Object>> threshList = (List) entry.getValue();
                    for (Map<String, Object> threshMap : threshList) {
                        for (Map.Entry<String, Object> threshEntry : threshMap.entrySet()) {
                            if (threshEntry.getKey().equals("value"))
                                threshold = new Long((int)threshEntry.getValue());
                            if (threshEntry.getKey().equals("operator"))
                                operator = Operator.getOperator((String) threshEntry.getValue());
                            if (threshEntry.getKey().equals("kafka_event_topic"))
                                kafkaTopic = (String) threshEntry.getValue();
                            if (threshEntry.getKey().equals("event"))
                                event = (String) threshEntry.getValue();
                            if (threshEntry.getKey().equals("data_fields")) {
                                List<Map<String, String>> xpathList = (List) threshEntry.getValue();
                                for (Map<String, String> xpathMap : xpathList) {
                                    for (Map.Entry<String, String> xpath : xpathMap.entrySet()) {
                                        xpaths.add(xpath.getValue());
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    public String getKafkaTopic() {
        return kafkaTopic;
    }

    public void setKafkaTopic(String kafkaTopic) {
        this.kafkaTopic = kafkaTopic;
    }

    public boolean isEvaluated() {
        return evaluate;
    }



    public long getThreshold() {
        return threshold;
    }

    public void setThreshold(long threshold) {
        this.threshold = threshold;
    }

    public Operator getOperator() {
        return operator;
    }

    public void setOperator(Operator operator) {
        this.operator = operator;
    }

    public String getEvent() {
        return event;
    }

    public void setEvent(String event) {
        this.event = event;
    }

    public List<String> getXpaths() {
        return xpaths;
    }

    public void setXpaths(List<String> xpaths) {
        this.xpaths = xpaths;
    }
}
