# Constants for the project


USERNAME = 'team.neurofinder@brainstormil.com'
PASSWORD = 'neurofinder23!!'

key_words_files = ['brain1.csv', 'brain2.csv', 'brain3.csv',
                   'mental health.csv', 'psychology.csv', 'neurotech.csv',
                   'cognitive1.csv', 'cognitive2.csv',
                   'neuroscience1.csv', 'neuroscience2.csv',
                   'cognition2.csv', 'cognition3.csv', 'cognition4.csv',
                   'neuro1.csv', 'neuro2.csv', 'neuro3.csv', 'neuro4.csv', 'neuro5.csv']

old_companies = [
    "Amygdala", "ANeuSTART", "Anyverse Studio", "Asio Advanced Control Solutions", "BWith AI", "Coach The Bot",
    "Cybernite", "ELEFense", "Epeius Pharma Ltd.", "FlatWorld", "ForSight Robotics", "Fresh Podcast Network",
    "Ginat Geshem", "GoodDeeds.AI", "Hexatone Finance", "HighRad Ltd.", "Inretio Medical Device", "Ixtlan Bioscience",
    "Kai.ai", "Logical Commander", "Mad Brain Games", "Metapsy", "MindSense", "Nanocarry", "Neuro Help", "PainPal",
    "Perceive Brain Health", "Pery/ Periapt", "Phi-G", "platera.ai", "Psyable", "Sanga", "Sency", "Snowflix/ Poppins",
    "SPHEREO", "Synergym.Ai", "timbr.ai", "Topicx Customer Experience Systems", "BrainWatch Tech", "Clearmind Medicine",
    "Cognitiv Neurosystems", "ELDA BrainTech", "Mood House", "N.T.W Power Boost", "Neurogait", "Neurotrigger",
    "NurExone Biologic", "Remepy", "Revium Recovery", "Cognyxx Pharmaceuticals", "AlgoSensus", "Anycan-technology",
    "Algobrain", "Applied Cognitive Engineering /IntelliGym", "Arrows", "AVertto", "Bpaus",
    "Calmigo/Dendro Technologies Inc", "Eleos Health", "Eye-minders", "Head Habitat", "Helping Minds", "Immunity Pharma",
    "Prilenia", "PsyRx Ltd", "Sensegait", "Talkspace", "WonderBrain Technologies", "Yalmo", "MemoBoost", "PamBio",
    "Galimedix Therapeutics", "RecallCue", "Aneuscreen", "Biomarkerz", "BrainWatch Tech", "Clearmind Medicine", "Cognitiv Neurosystems", "Dase",
    "ELDA BrainTech", "eMazeLabs", "Exegiline Pharma", "iFocus Health", "Madrigal Mental Care Ltd", "MemoApp", "Mindtension",
    "Mood House", "N.T.W Power Boost", "Neurogait", "Neurotrigger", "NucleoTech", "NurExone Biologic", "Remepy", "Revium Recovery",
    "Short Wave Pharma", "SlimTarget Medical", "Wellplay", "ViTAs Labs", "Topicx", "Thermanostics", "Tamarix Pharma",
    "SynCath NeuroScience", "Symetrify", "Skelable", "Sequel.Care", "Selene Therapeutics", "NuroTone Medical",
    "Motiv8 Technologies", "Glixogen Therapeutics", "Feel Right", "Eyecuracy", "CVAid Medical",
    "Cognyxx Pharmaceuticals", "CogniFiber", "Clexio Biosciences", "Ascento Medical", "APPLicodrama", "AlgoSensus",
    "Actics Medical", "aidymo-cv", "AIO", "AlgoSensus", "Alpe Audio", "APPLicodrama", "Arcana Instruments", "Artbrain",
    "ASAT - As Simple As That", "Ascento Medical", "Autobrains", "Beewizer", "Beyeonics", "BioT Medical", "C-Crop",
    "Cannamore Biotechs", "Cecilia.ai", "cinten", "CityEars", "Clearya", "Clexio Biosciences", "CogniFiber",
    "Cognyxx Pharmaceuticals", "COMMUNi", "Conbo.ai", "Crispr Stem & Therapeutics (CST)", "CTHal", "CVAid Medical",
    "DeeDz", "DeePathology.ai", "Docet TI", "DOConvert", "Dtect Vision", "EGAIA", "Endoways", "Evolution.inc",
    "Eyecuracy", "Feel Right", "Fibo", "Finq", "Flymingo", "Frenel Imaging", "Genda", "GeoCloud", "GiantLeap",
    "Glixogen Therapeutics", "Hi Auto", "Hyro", "IDEEZA", "IMCI Pharmaceuticals", "Immunai", "InShop", "Intonation AI",
    "Kaleidoo", "KanduAI", "Kardome Technology", "Keylabs AI", "Lasting Effect Consumer Pharma", "liveAtip",
    "Loopback AI", "Louie7.AI", "MagniLearn", "Makalu Optics", "Matricelf", "MetaSight Diagnostics", "Momentick",
    "Motiv8 Technologies", "MultiKol B.T", "MultiVu", "N.I.P UP", "Name", "Neolithics", "NeuReality",
    "Neuronix AI Labs", "NINA Medical", "Novacy", "NuroTone Medical", "Nutek", "Obrecsys", "OpenDNA", "PeersMD", "Pimea Allergy",
    "Pixend", "Platera.ai", "Polyn Technology", "prespro.ai", "Saiflow Cyber", "SBN Signature Biometrics", "Selectika",
    "Selene Therapeutics", "Sequel.Care", "ShanenLi", "sidely", "SightBit", "Skelable", "Symetrify", "SynCath NeuroScience",
    "Table44", "Tamarix Pharma", "Teeki", "The Digital Pets Company", "Theia Vision AI", "Thermanostics", "Topicx",
    "Trough.AI", "Trullion", "UB Therapeutics", "UGlabs", "Usearch", "Visionary.ai", "Visual Layer", "ViTAs Labs",
    "VIVID", "Weedex", "Wide Therapy", "WMH", "X-tend Robotics", "Yevul Info", "ZIMARK", "ANYCAN TECHNOLOGY", "Anyverse",
    "Biomarkerz", "Bold", "BrainWatch Tech", "Clearmind Medicine", "Cognishine Therapy and Education",
    "Cognitiv Neurosystems", "Corsight", "Dase", "ELDA BrainTech", "eMazeLabs", "Exegiline Pharma", "GoodDeeds", "iBrainy",
    "iFocus Health", "Ixtlan BioScience", "Jiniz", "Kai", "Lean AI", "Ludeo", "Mad Brain Games", "Madrigal Mental Care",
    "Medicane Health", "MemoApp", "MindOverMatteR", "Mindtension", "Mood House", "Muuula Games", "N.T.W Power Boost", "Name", "NanoGhost",
    "Nervio", "Neurogait", "NovaPulse", "NucleoTech", "NurExone Biologic", "Periapt", "PsyRx", "QualiTalk", "Remepy",
    "Revium Recovery", "Rise", "Serojec", "SHOPPER AI", "Short Wave Pharma", "SlimTarget Medical", "TABI Learning Technologies",
    "Wellplay", "ForSight Robotics", "TABI", "Pery", "Sency.", "Anyverse Studio", "Inretio Medical Device",
    "platera.ai",
    "Anicca Health", "Synergym.Ai", "BWith AI", "Kai.ai", "PainPal", "GoodDeeds.AI", "Epeius Pharma Ltd.", "Nano Carry",
    "Topicx Customer Experience Systems", "CoachAi", "NeuroQuest", "SPHEREO", "Heat Intelligence", "CogMe", "Evature",
    "Treato", "Otorize LTD", "Neurotech Solutions", "Eco Fusion", "Innosphere", "Sanga", "Excellent Brain",
    "HeadSense Medical", "SensoMedical", "Head Habitat", "Video Inform", "Onvego", "Neuromagen Pharma", "ProCore",
    "IDC Herzliya - Zell Entrepreneurship", "FlatWorld.co", "Ludus Materials ltd", "Digital Trowel",
    "MTRE Advanced Technologies Ltd.", "QuantalX", "Psyable", "Kideo Tech", "Magna BSP", "Prospec", "ELEFense",
    "BrainVu",
    "Ceretrieve", "Cybernite", "Mixers", "Braincast", "Medoc", "Metapsy", "Bioimmunate", "Qrative", "Lipogen",
    "Israel Brain Technologies", "Mindguard", "Surpass Medical", "Perceive Brain Health", "Cognilyze", "MindSense",
    "NeuroIndex", "Hexatone Finance", "Salead", "Odin Medical Technologies", "ClearForest", "Brain1 Ltd", "ERAN",
    "Snowflix", "Visior Technologies Ltd.", "Mind Innovations", "GG Apps", "Ixtlan Bioscience", "shopUpz",
    "Brainose Technologies", "Salute Rehab", "Herzog Hospital", "kmoEye", "Nathan", "CognitiveID", "Ctx Platforms",
    "OmegaMore", "Coach The Bot", "GeneGrafts", "Gigantt", "HighRad Ltd.", "Musli Thyropeutics", "SynCath NeuroScience",
    "Get Help Israel", "Biomarkerz", "Clara Mind", "NeuroAudit Ltd.", "InnoVision Labs", "IDD Therapeutics",
    "Optical Imaging", "Spero Biopharma", "Planet of the Apps", "AttenGo", "ANeuSTART", "iBuddy", "Makshivim Net",
    "Roots",
    "Libra@Home", "CogAid", "Insight Sparks", "Tipulog", "Emelai", "Wombat", "Zinuk Schools", "Sela Medical",
    "Fresh Podcast Network", "4Girls", "Nibs", "Tetrax", "PValueHR", "Decodea", "Hug and Dug", "GMH FOR SINGLES APP",
    "Fullest", "Referante", "Yowza", "Do 4 Brain", "eSistence Virtual Interaction", "I-Traffix", "Phi-G",
    "Abracadabra Robotics", "Neuro vision", "Tradis Gat", "Asio Advanced Control Solutions", "Brainster",
    "Targeted Modulated Sound Therapy", "Jung", "mAIndo", "The Learning Works", "FITS",
    "Sagol Center for Brain and Mind",
    "CogniZance", "Imexco", "Linguistic Agents", "Revealers App", "Neanic Healthineers & Consultant Private Limited",
    "ApexNano Medical", "JOYA 4U", "Amygdala", "Mental Heal", "Katkuti", "ALYN Woldenberg Family Hospital", "HybRead",
    "ListenUp Technologies", "NeuroPet", "NAN Instruments", "mmcubit", "A-muse", "TreTone", "Sagacity Systems", "myRay",
    "PsychoMaster", "Neuro Help", "Chooze", "BiondMetric", "Ooja", "Thiel International", "The Sport Psychology Center"
]

"""
Company_Name
Updating_Date
Logo in Visualization folder?
Operation Status (Active=True, False = False)
INCLUSION
Operation/relevant Notes
Company_Website
Startup Nation Page
Neurotech_Category
Market_Category	Target_Market
TechTools_1
TechTools_2
TechTools_3
Description
Full Description
CB (CrunchBang) Link
Company CB Categories
Company_Location
Company_Founded_Year
Company_Number_of_Employees
Company_CB_Rank
Funding_Status
Last_Funding_Type
Last_Funding_Date
Last_Funding_Amount
Total_Funding_Amount
Total_Funding_Amount_M_dollars
Number_of_Funding_Rounds
Estimated_Revenue_Range
Company_Number_of_Investors
Company_Number_of_Investments
Company LinkedIn Link
Company_LinkedIn_Followers_Number
Company Contact Email
Company phone number
Founders
CSO
CTO
CEO
COO
CFO
Co-Founder
President
Team Members
Address
former company names
acquired
product_stage
Comments
"""

"""
Name
Finder URL
Description
Primary Sector
Founded
Employees
Funding Stage
"""
