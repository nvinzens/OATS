package client.model;

import java.util.List;

public class OATSArgs {
    private static String inputTopic;
    private static String outputTopic;
    private static long threshold;
    private static Operator operator;
    private static String rootXpath;
    private static String nameXpath;

    public static void setInputTopic(String inputTopic) {
        OATSArgs.inputTopic = inputTopic;
    }

    public static void setOutputTopic(String outputTopic) {
        OATSArgs.outputTopic = outputTopic;
    }

    public static void setThreshold(long threshold) {
        OATSArgs.threshold = threshold;
    }

    public static void setOperator(Operator operator) {
        OATSArgs.operator = operator;
    }

    public static void setRootXpath(String rootXpath) {
        OATSArgs.rootXpath = rootXpath;
    }

    public static void setNameXpath(String nameXpath) {
        OATSArgs.nameXpath = nameXpath;
    }

    public static void setDataXpath(String dataXpath) {
        OATSArgs.dataXpath = dataXpath;
    }

    public void setStatStateStore(String statStateStore) {
        this.statStateStore = statStateStore;
    }

    private static String dataXpath;

    private String statStateStore;

    public OATSArgs(String[] args) {
        try {

            inputTopic = args[0];
            outputTopic = args[1];
            threshold = Long.parseLong(args[2]);
            operator = Operator.getOperator(args[3]);
            rootXpath = args[4];
            nameXpath = args[5];
            dataXpath = args[6];
            statStateStore = inputTopic + "-statestore";
        } catch (Exception e) {
            System.out.println(e.toString());
            System.err.println("Exception while reading arguments. Order or amount of arguments might be wrong");
            System.err.println("Jar expects 7 args. Given args: " + args.length);
            System.exit(1);
        }
    }

    public String getInputTopic() {
        return inputTopic;
    }

    public String getOutputTopic() {
        return outputTopic;
    }

    public long getThreshold() {
        return threshold;
    }

    public Operator getOperator() {
        return operator;
    }

    public String getRootXpath() {
        return rootXpath;
    }

    public String getNameXpath() {
        return nameXpath;
    }

    public String getDataXpath() {
        return dataXpath;
    }

    public String getStatStateStore() {
        return statStateStore;
    }
}
