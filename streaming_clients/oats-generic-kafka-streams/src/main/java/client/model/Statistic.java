package client.model;

public class Statistic {

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

    public static boolean filterNonZero(String key, Statistic stat) {
        return stat.getOutDiscards() != 0 && key != null;
    }

    public boolean isAboveThreshold(Statistic oldStat, long threshold) {
        return (this.getOutDiscards() - oldStat.getOutDiscards()) > threshold;
    }
}
