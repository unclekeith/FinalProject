from gtts import gTTS

text = """Hello!
Welcome to Embakwe Aziwe, your next generation school enrollment system.
Designed to enroll students into the Ordinary and Advanced level classes at Embakwe High school.
Look around and feel comfortable with our smooth UI designed in python.
Have a great time as our motto says. Aziwe laa.
"""

tts = gTTS(text=text, lang="en")

tts.save("Aziwe.mp3")
