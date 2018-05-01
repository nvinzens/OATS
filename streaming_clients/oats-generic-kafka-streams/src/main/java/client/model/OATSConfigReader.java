package client.model;

import java.util.List;
import java.util.Map;

public class OATSConfigReader {
    private List<Map<String, Object>> hosts;
    private List<Map<String, Object>> subscriptions;

    public void setHosts(List<Map<String, Object>> hosts) {
        this.hosts = hosts;
    }

    public void setSubscriptions(List<Map<String, Object>> subscriptions) {
        this.subscriptions = subscriptions;
    }

    public List<Map<String, Object>> getHosts() {
        return hosts;
    }

    public List<Map<String, Object>> getSubscriptions() {
        return subscriptions;
    }
}
