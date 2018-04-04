
package streamclients.util;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public class MemoryStatistic {

    private String eventTime;
    @JsonProperty("memory-statistic")
    private Map<String, Long> memoryStatistic;

    public void setEventTime(String eventTime) {
        this.eventTime = eventTime;
    }

    public String getEventTime() {
        return eventTime;
    }

    public void setMemoryStatistic(Map<String, Long> memoryStatistic) {
        this.memoryStatistic = memoryStatistic;
    }

    public Map<String, Long> getMemoryStatistic() {
        return memoryStatistic;
    }

    @Override
    public String toString() {
        String string = "EventTime " + eventTime + "\nMemoryStatics:\n";
        for (Map.Entry<String, Long> entry : memoryStatistic.entrySet()) {
            string += "    Process " + entry.getKey() + ": used memory: " + entry.getValue() + "\n";
        }
        return string;
    }
}
