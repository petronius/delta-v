import random

SHIP_NAMES = """
ESEC Amaro Pargo
ESEC Erebus
ESEC Liverpool Packet
ESEC William Kidd
ESEC Estelle
ESEC Abram Petrovich Gannibal
ESEC De Zeven Provinciën
ESEC Don Quixote
ESEC The First Sally
ESEC The Second Sally
# Stanisław Lem-class
ESEC Stanisław Lem
ESEC Trurla i Klapaucjusza
ESEC Hispital of the Transfiguration
ESEC Man from Mars
ESEC Megallanic Cloud
ESEC Memoirs Found in a Bathtub
ESEC Solaris
ESEC Return from the Starts
ESEC Eden
ESEC Chain of Chance
ESEC Futurological Congress
ESEC Golem XIV
ESEC Observation on the Spot
ESEC Fiasco
ESEC Peace on Earth
ESEC Imaginery Magnitude
ESEC Mortal Engines
ESEC Perfect Vaccum
ESEC Pirx the Pirate
ESEC One Human Minute
ESEC Provocation
#
# 
#
ACSA Young Teazer's Ghost
ACSA T Kieth Glennan
ACSA Carl E Sagan
ACSA Dava Newman
ACSA Elcid Barett
ACSA Agustín de Iturbide
ACSA Toquinho
ACSA Espírito Santo
#
#
#
SESA Yellow River/黃河
SESA Aurangzeb
SESA Hakudo Maru/白童丸
SESA Zhèng Hé/鄭和
# Genji-class
SESA Genji
SESA Shell of the Locust
SESA Evening Faces
SESA Young Murasaki
SESA Autumn Excursion
SESA Sacred Tree
SESA Village of Falling Flowers (Falling Flowers)
SESA Exile to Suma
SESA Flood Gauge
SESA Palace of the Tangled Woods (Tangled Woods)
SESA A Meeting at the Fronteir (Frontier)
SESA Picture Contest
SESA Wind in the Pines
SESA Rack of Clouds
SESA Maidens of the Dance
SESA Tendril Wreath
SESA First Song of the Year
SESA Wild Carnation
SESA Cresset Fires
SESA Autumn Tempest
SESA Imperial Progress
SESA Cypress Pillar
SESA Early Spring Genesis
SESA Transverse Flute
SESA Bell Cricket
SESA Evening Mist
SESA Rites of Sacred Law
SESA Sprit Summoner
SESA Vanished into the Clouds
SESA Bamboo River
SESA Divine Princess at Uji Bridge
SESA A Hut in the Eastern Provinces (Eastern Provinces)
SESA A Boat Cast Adrift
SESA Writing Practice
#
#
#
ALSA Nebudchadnezzar II
ALSA Al-Hashimiyun
ALSA Gamal Abdel Nasser Husseni
# Omar Khayyam-class
ALSA Omar Khayyam
ALSA Chasing the Temporal
ALSA The Lion and the Lizard
ALSA In the Presence of Flowers
ALSA Fire of Spring
ALSA Great Argument
ALSA Dawn's Left Hand
ALSA A Garden by the Water
ALSA Nights and Days
ALSA Hunter of the East
ALSA Morning in the Bowl of Night
#
# Titan corp
#
TNV The Blank Cheque
TNV The Banquet
TNV Attempting the Impossible
TNV Invention of Life
TNV The Pilgrim
TNV Castle in the Pyrenees
TNV Elective Affinities
TNV Empire of Light
TNV Empty Mask
TNV Golnconda
TNV Natural Encounters
TNV On the Threshold of Liberty
TNV Personal Values
TNV Son of Man
TNV Birth of the Idol
TNV False Mirror
TNV Gradation of Fire
TNV The Lost Jockey
TNV Mysteries of the Horizon
TNV Titanic Days
TNV Trechery of Images
TNV Threatened Assasin
TNV Battle of Argonne
TNV Therapist
TNV Memory of a Voyage
"""

SHIP_NAMES = SHIP_NAMES.splitlines()
SHIP_NAMES = filter(lambda x: x and not x.startswith("#"), [name.strip() for name in SHIP_NAMES])
SHIP_NAMES = list(SHIP_NAMES)

def random_ship_name():
    return random.choice(SHIP_NAMES)