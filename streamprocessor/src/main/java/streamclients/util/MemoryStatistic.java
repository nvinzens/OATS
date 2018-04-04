
package streamclients.util;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public class MemoryStatistic {

    private String eventTime;

    private Map<String, String> memoryStatistic;

    public void setEventTime(String eventTime) {
        this.eventTime = eventTime;
    }

    public String getEventTime() {
        return eventTime;
    }

    public void setMemoryStatistic(Map<String, String> memoryStatistic) {
        this.memoryStatistic = memoryStatistic;
    }

    public Map<String, String> getMemoryStatistic() {
        return memoryStatistic;
    }

    @Override
    public String toString() {
        return "EventTime: " + eventTime + ", MemoryStatistic: " + memoryStatistic;
    }
}
