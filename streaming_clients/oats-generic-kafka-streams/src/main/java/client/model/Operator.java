package client.model;

public enum Operator {


    GREATER_THAN, SMALLER_THAN, EQUALS,
    GREATER_OR_EQUAL, SMALLER_OR_EQUAL;

    /**
     * Takes a string and returns an Operator
     * @param code the code that identifies an Operator, eg. "greater_than"
     * @return
     */
    public static Operator getOperator(String code) {

        switch (code) {
            case "greater_than":
                return GREATER_THAN;
            case "smaller_than":
                return SMALLER_THAN;
            case "equals":
                return EQUALS;
            case "greater_or_equal":
                return GREATER_OR_EQUAL;
            case "smaller_or_equal":
                return SMALLER_OR_EQUAL;
            default:
                throw new EnumConstantNotPresentException(Operator.class, "Operator " + code + " provided in config file is invalid.");
        }
    }
}
