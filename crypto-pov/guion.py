# Ep.1 "You Wake Up in 2009 Knowing Everything About Bitcoin" (inglés, 16:9 para X)
# La narración (Titan) es UN solo audio: narr.mp3. Se corta en tramos por los tiempos de whisper y se recoloca con
# huecos para las otras voces. ("id", quién, texto de la narración / del clip)
#   N = narrador (Titan)  Y = tú (misma voz Titan)  D = papá (Justin)  V = tele (presentador)
LINEAS = [
    ("N01", "N", "You go to sleep in 2026. You wake up in 2009. And you know exactly what Bitcoin is going to become."),
    ("N02", "N", "An alarm clock rings. Not your phone. A real alarm clock."),
    ("N03", "N", "This isn't your apartment. Posters on the wall. A huge, ugly monitor. A flip phone on the desk."),
    ("N04", "N", "The date reads... January 9th, 2009."),
    ("N05", "N", "You run to the mirror. You're nineteen again."),
    ("N06", "N", "Downstairs, the TV is on."),
    ("V01", "V", "Banks are collapsing across the country. Millions of Americans have lost their homes..."),
    ("D01", "D", "Money isn't safe anywhere anymore."),
    ("N07", "N", "And then it hits you. Six days ago, someone called Satoshi Nakamoto mined the very first Bitcoin block."),
    ("N08", "N", "Almost nobody on Earth knows it exists."),
    ("N09", "N", "Right now, one Bitcoin is worth... zero dollars. In your future, one was worth over a hundred thousand."),
    ("N10", "N", "You check your bank account. Three hundred and forty dollars. That's your entire fortune."),
    ("Y01", "Y", "Dad... what if I told you there's a new kind of money? Digital. No banks. And one day it'll be worth millions?"),
    ("D02", "D", "Son... go get a job."),
    ("N12", "N", "Night. Everyone's asleep. You turn on the old family computer. The fan screams like a jet engine."),
    ("N13", "N", "On a tiny cryptography mailing list, you find it. Bitcoin. Version zero point one. Released today."),
    ("N14", "N", "You download it. Click Generate Coins. Fifty bitcoins per block."),
    ("N15", "Y", "This time... I'm not missing it."),
    ("N16", "N", "Three twelve A.M. The screen flickers. A message appears. No name. No sender. Just six words."),
    ("N17", "N", "I know where you came from."),
    ("N18", "N", "Your blood freezes. Nobody knows. Nobody can know."),
    ("N19", "N", "So what do you do? A... you reply, and find out who knows your secret. Or B... you delete it, and keep mining like nothing happened."),
    ("N20", "N", "Comment A or B. The story continues... with what you choose."),
]

# clips que NO están en narr.mp3: archivo propio (si existe) o hueco con el texto en pantalla
CLIPS = {"V01": "tv.mp3", "D01": "dad1.mp3", "D02": "dad2.mp3"}
HUECO_SIN_AUDIO = {"V01": 3.6, "D02": 2.4}
