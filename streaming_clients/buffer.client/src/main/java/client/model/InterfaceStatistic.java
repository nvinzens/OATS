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

    public static boolean filterNonZero(String key, InterfaceStatistic stat) {
        return stat.getOutDiscards() != 0 && key != null;
    }

    public boolean isAboveThreshold(InterfaceStatistic oldStat, long threshold) {
        return (this.getOutDiscards() - oldStat.getOutDiscards()) > threshold;
    }
}
