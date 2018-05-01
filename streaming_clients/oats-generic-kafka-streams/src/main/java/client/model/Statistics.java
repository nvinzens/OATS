package client.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.time.Instant;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Statistics {

    private Instant eventTime;
    private List<Statistic> ifaceStatistics;

    public void setEventTime(String eventTime) {
        this.eventTime = Instant.parse(eventTime);
    }

    public Instant getEventTime() {
        return eventTime;
    }

    public void setIfaceStatistics(List<Statistic> ifaceStatistics) {
        this.ifaceStatistics = ifaceStatistics;
    }

    public List<Statistic> getIfaceStatistics() {
        return ifaceStatistics;
    }
}
