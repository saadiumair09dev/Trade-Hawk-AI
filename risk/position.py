def position_size(confidence):
    if confidence >= 80:
        return 1.0
    elif confidence >= 65:
        return 0.5
    elif confidence >= 55:
        return 0.25
    return 0

def risk_label(size):
    if size == 1.0:
        return "HIGH"
    elif size == 0.5:
        return "MEDIUM"
    elif size == 0.25:
        return "LOW"
    return "NO TRADE"
