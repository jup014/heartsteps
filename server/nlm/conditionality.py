def always_true_conditionality():
    """This is a sample conditionality. Don't erase it. Don't use it for other than testing purpose.

    Returns:
        boolean: return the conditionality.
    """
    return True

def Random_50_50_log():
    """This is a sample conditionality with logging. Don't erase it. Don't use it for other than testing purpose.

    Returns:
        boolean: return the conditionality.
    """
    import random
    import json
    from nlm.services import LogService
    
    random_value = random.random()
    threshold_value = 0.5
    
    logger = LogService(subject_name="Random_50_50_log")
    logger.log(value=json.dumps({
        "name": "random value", 
        "value": (random_value > threshold_value),
        "support_evidences": {
            "random_value": random_value,
            "threshold": threshold_value
            }
        }), purpose="test purpose", object="test object")
    
    