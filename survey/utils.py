# Utility functions used across this app!

# round stored values to 3 decimal places for
# better human readability of the data dumps
def sanely_rounded(float):
    return round(float, 3)
