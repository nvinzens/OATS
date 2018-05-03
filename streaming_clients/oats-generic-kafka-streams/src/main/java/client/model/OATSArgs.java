package client.model;

import java.util.List;

public class OATSArgs {
    private static String inputTopic;
    private static String outputTopic;
    private static long threshold;
    private static Operator operator;
    public static String rootXpath;
    public static String nameXpath;
    public static String dataXpath;

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
