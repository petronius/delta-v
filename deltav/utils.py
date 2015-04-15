
import random

SHIP_NAMES = """
Nervous Energy 
Prosthetic Conscience 
The Ends Of Invention 
Eschatologist 
Irregular Apocalyse 
No More Mr Nice Guy 
Determinist 
Bora Horza Gobuchul 
Profit Margin 
Trade Surplus 
Revisionist 
Screw Loose 
Flexible Demeanour 
Just Read The Instructions 
Of Course I Still Love You 
Limiting Factor 
Cargo Cult 
Little Rascal 
So Much For Subtlety 
Unfortunate Conflict Of Evidence 
Youthful Indiscretion 
Gunboat Diplomat 
Zealot 
Kiss My Ass 
Prime Mover 
Just Testing 
Xenophobe 
Very Little Gravitas Indeed 
What Are The Civilian Applications? 
Congenital Optimist 
Size Isn't Everything 
Sweet and Full of Grace 
Different Tan 
Fate Amenable To Change 
Grey Area 
It's Character Forming 
Jaundiced Outlook 
Problem Child 
Reasonable Excuse 
Recent Convert 
Tactical Grace 
Unacceptable Behaviour 
Steely Glint 
Highpoint 
Shoot Them Later 
Attitude Adjuster 
Killing Time 
Frank Exchange Of Views 
Anticipation Of A New Lover's Arrival, The 
Death and Gravity 
Ethics Gradient 
Honest Mistake 
Limivourous 
No Fixed Abode 
Quietly Confident 
Sleeper Service 
Uninvited Guest 
Use Psychology 
What Is The Answer and Why? 
Wisdom Like Silence 
Yawning Angel 
Zero Gravitas 
Misophist 
Serious Callers Only 
Not Invented Here 
Appeal To Reason
Break Even
Long View
Peace Makes Plenty
Sober Counsel
Within Reason
Kiss the Blade 
Frightspear
Furious Purpose
Riptalon
Wingclipper
SacSlicer II
Xenoclast
Full Refund 
Charitable View 
Just Passing Through 
Added Value
I Blame Your Mother
I Blame My Mother
Heavy Messing 
Bad for Business 
Arbitrary 
Cantankerous 
Only Slightly Bent 
I Thought He Was With You 
Space Monster 
A Series Of Unlikely Explanations 
Big Sexy Beast 
Never Talk To Strangers 
Funny, It Worked Last Time... 
Boo! 
Ultimate Ship The Second 
It'll Be Over By Christmas 
A Ship With A View
Ablation
Arrested Development
Credibility Problem
Dramatic Exit
Excuses And Accusations
God Told Me To Do It
Halation Effect
Happy Idiot Talk
Helpless In The Face Of Your Beauty
Heresiarch
Just Another Victim Of The Ambient Morality
Minority Report
Not Wanted On Voyage
Perfidy
Sacrificial Victim
Stranger Here Myself
Synchronize Your Dogmas
Thank you And Goodnight
The Precise Nature Of The Catastrope
Unwitting Accomplice
Undesirable Alien
Well I Was In The Neighbourhood
You Would If You Really Loved Me
You'll Thank Me Later
Winter Storm 
Piety 
Nuisance Value 
Vulgarian 
Sanctioned Parts List 
Resistance Is Character-Forming 
From the conversation:
All Through With This Niceness And Negotiation Stuff 
Someone Else's Problem
Lacking That Small Match Temperament
Poke It With A Stick 
I Said, I've Got A Big Stick 
Hand Me The Gun And Ask Me Again
But Who's Counting?
Germane Riposte
We Haven't Met But You're A Great Fan Of Mine
All The Same, I Saw It First
Ravished By The Sheer Implausibility Of That Last Statement
Zero Credibility
Charming But Irrational
Demented But Determined
You May Not Be The Coolest Person Here
Lucid Nonsense
Awkward Customer
Thorough But ... Unreliable
Advanced Case Of Chronic Patheticism
Another Fine Product From The Nonsense Factory
Conventional Wisdom
In One Ear
Fine Till You Came Along
I Blame The Parents
Inappropriate Response
A Momentary Lapse Of Sanity
Lapsed Pacifist
Reformed Nice Guy
Pride Comes Before A Fall
Injury Time
Now Look What You've Made Me Do
Kiss This Then
Grey Area/Meatfucker
Soulhaven 
Lasting Damage 
Lasting Damage I 
Lasting Damage II 
Experiencing A Significant Gravitas Shortfall 
"""

PLANET_NAMES = """
Aquaria
Canceron
Caprica
Algae Planet
Cyrannus
Cylon Homeworld
Djerba
Earth
Kobol
Gememnon
Icarus
Hebe
Nike
Picon
Tauron
Minos
Erebos
Zeus
Persephone
"""

def random_ship_name():
    return random.choice(list(filter(None, SHIP_NAMES.splitlines())))

def random_planet_name():
    return random.choice(list(filter(None, PLANET_NAMES.splitlines())))