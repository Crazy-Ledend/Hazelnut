import random

# shade-pool for embeds
shades = [
    "7FFFFF", "59E5E5",  # Lighter blues
    "8CFFFF", "4FCCCB",
    "99FFFF", "46B2B2",
    "A6FFFF", "3C9999",
    "B3FFFF", "328080",
    "C0FFFF", "296666",
    "CCFFFF", "204D4D",
    "D9FFFF", "163333",
    "3366FF", "1E90FF", 
    "4682B4", "5F9EA0",
    "6495ED", "7B68EE",  
    "6A5ACD", "4169E1",  
    "0000CD"
]


def embed():
    # Generate a random color
    random_color = random.choice(shades)
    return random_color