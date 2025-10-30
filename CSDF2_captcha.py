# Importing the ImageCaptcha class from captcha.image module
# Used to generate CAPTCHA images
from captcha.image import ImageCaptcha

# Importing random module to randomly select characters
import random

# Function to generate a random CAPTCHA string of length n
def generateCaptcha(n):
    # Possible characters: lowercase, uppercase letters and digits
    chrs = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    captcha = ""
    # Loop to randomly choose characters and form a CAPTCHA text
    for _ in range(n):
        captcha += chrs[random.randint(0, 61)]  # random index between 0 and 61
    return captcha

# Function to check if user input matches the generated CAPTCHA
def checkCaptcha(captcha, user_captcha):
    # Returns True if both strings are same, else False
    return captcha == user_captcha

# Main code block
if __name__ == "__main__":
    n = 8  # length of CAPTCHA text

    # Generate a random captcha text
    captcha_text = generateCaptcha(n)
    print("Generated Captcha Text:", captcha_text)

    # Create a CAPTCHA image object with given width and height
    image = ImageCaptcha(width=200, height=90)

    # Save the CAPTCHA image as 'CAPTCHA.png'
    image.write(captcha_text, 'CAPTCHA.png')
    print("Captcha image saved as CAPTCHA.png. Open it to view.")

    # Ask user to enter what they see in the image
    user_captcha = input("Enter the captcha: ")

    # Check whether user-entered text matches the original CAPTCHA
    if checkCaptcha(captcha_text, user_captcha):
        print("CAPTCHA Matched!")     # correct input
    else:
        print("CAPTCHA Not Matched!") # wrong input
