def calculate_fringe(hours_worked, fringe_rate):
    """
    Compute fringe benefit amount: hours * fringe_rate.
    Returns a float rounded to 2 decimal places.
    """
    return round(hours_worked * fringe_rate, 2)
