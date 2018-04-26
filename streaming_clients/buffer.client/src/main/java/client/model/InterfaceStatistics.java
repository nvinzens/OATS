package client.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import javafx.util.Pair;

import java.time.Instant;
import java.util.List;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public class InterfaceStatistics {

    private Instant eventTime;
    private List<InterfaceStatistic> ifaceStatistics;

    public void setEventTime(String eventTime) {
        this.eventTime = Instant.parse(eventTime);
    }

    public Instant getEventTime() {
        return eventTime;
    }

    public void setIfaceStatistics(List<InterfaceStatistic> ifaceStatistics) {
        this.ifaceStatistics = ifaceStatistics;
    }

    public List<InterfaceStatistic> getIfaceStatistics() {
        return ifaceStatistics;
    }
}
