package client.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.time.Instant;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Statistics {

    private Instant eventTime;
    private List<Statistic> statistics;

    public void setEventTime(String eventTime) {
        this.eventTime = Instant.parse(eventTime);
    }

    public Instant getEventTime() {
        return eventTime;
    }

    public void setStatistics(List<Statistic> statistics) {
        this.statistics = statistics;
    }

    public List<Statistic> getStatistics() {
        return statistics;
    }
}
