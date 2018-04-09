package client.model;

public class InterfaceStatistic {

    private String ifaceName;
    private long outDiscards;

    public long getOutDiscards() {
        return outDiscards;
    }

    public String getIfaceName() {
        return ifaceName;
    }

    public void setIfaceName(String ifaceName) {
        this.ifaceName = ifaceName;
    }

    public void setOutDiscards(long outDiscards) {
        this.outDiscards = outDiscards;
    }
}
