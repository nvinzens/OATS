package client.model;

public class Statistic {

    private String name;
    private long value;

    public long getValue() {
        return value;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setValue(long value) {
        this.value = value;
    }

    public static boolean filterNonZero(String key, Statistic stat) {
        return stat.getValue() != 0 && key != null;
    }

    public boolean isAboveThreshold(Statistic oldStat, long threshold) {
        return (this.getValue() - oldStat.getValue()) > threshold;
    }
}
