import os
import sqlite3

FS_ROOT = os.environ.get('FS_SOURCE_DIR', './fs_source_dir')

# Define directory structure
folders = [
    'home/admin/research',
    'home/admin/scripts',
    'data/exports',
    'var/log',
]

# Create directories
for folder in folders:
    os.makedirs(os.path.join(FS_ROOT, folder), exist_ok=True)

# Create SQLite databases with sample schema
def create_animals_db(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS animals (
        id INTEGER PRIMARY KEY,
        name TEXT,
        species TEXT,
        status TEXT,
        location TEXT,
        description TEXT
    )''')
    animals = [
        ('Lynx', 'Lynx lynx', 'Endangered', 'Carpathian Mountains', 'A solitary wild cat native to European forests.'),
        ('European Bison', 'Bison bonasus', 'Vulnerable', 'Bialowieza Forest', 'The heaviest surviving wild land animal in Europe.'),
        ('Amur Leopard', 'Panthera pardus orientalis', 'Critically Endangered', 'Russian Far East', 'One of the world’s rarest big cats.'),
        ('Mountain Gorilla', 'Gorilla beringei beringei', 'Endangered', 'Virunga Mountains', 'Large primate found in central Africa.'),
        ('Red Panda', 'Ailurus fulgens', 'Endangered', 'Eastern Himalayas', 'Small mammal with reddish-brown fur.'),
        ('Snow Leopard', 'Panthera uncia', 'Vulnerable', 'Central Asia', 'Well-camouflaged big cat of the mountains.'),
        ('Saola', 'Pseudoryx nghetinhensis', 'Critically Endangered', 'Annamite Range', 'Rarely seen bovine known as the "Asian unicorn".'),
        ('Javan Rhino', 'Rhinoceros sondaicus', 'Critically Endangered', 'Ujung Kulon National Park', 'One of the rarest large mammals.'),
        ('Sumatran Orangutan', 'Pongo abelii', 'Critically Endangered', 'Sumatra', 'Great ape native to Indonesia.'),
        ('Hawksbill Turtle', 'Eretmochelys imbricata', 'Critically Endangered', 'Tropical Oceans', 'Sea turtle known for its beautiful shell.'),
        ('Vaquita', 'Phocoena sinus', 'Critically Endangered', 'Gulf of California', 'World’s rarest marine mammal.'),
        ('Black-footed Ferret', 'Mustela nigripes', 'Endangered', 'North America', 'Small carnivorous mammal.'),
        ('Iberian Lynx', 'Lynx pardinus', 'Endangered', 'Iberian Peninsula', 'The world’s most endangered feline.'),
        ('Giant Panda', 'Ailuropoda melanoleuca', 'Vulnerable', 'China', 'Iconic bear with distinctive black and white coloring.'),
        ('Addax', 'Addax nasomaculatus', 'Critically Endangered', 'Sahara Desert', 'Desert antelope adapted to arid conditions.'),
        ('Blue Whale', 'Balaenoptera musculus', 'Endangered', 'Global Oceans', 'Largest animal ever known to have lived.'),
        ('Gharial', 'Gavialis gangeticus', 'Critically Endangered', 'Indian Subcontinent', 'Fish-eating crocodile with long snout.'),
        ('Asian Elephant', 'Elephas maximus', 'Endangered', 'South and Southeast Asia', 'Largest living land animal in Asia.'),
        ('Siberian Tiger', 'Panthera tigris altaica', 'Endangered', 'Russian Far East', 'Largest tiger subspecies.'),
        ('Grevy’s Zebra', 'Equus grevyi', 'Endangered', 'East Africa', 'Largest and most endangered zebra species.'),
        ('Northern Bald Ibis', 'Geronticus eremita', 'Endangered', 'North Africa, Middle East', 'Distinctive wading bird with bald head.'),
        ('Kakapo', 'Strigops habroptilus', 'Critically Endangered', 'New Zealand', 'Flightless nocturnal parrot.'),
        ('Hainan Gibbon', 'Nomascus hainanus', 'Critically Endangered', 'Hainan Island', 'World’s rarest primate.'),
        ('Yangtze Finless Porpoise', 'Neophocaena asiaeorientalis', 'Critically Endangered', 'Yangtze River', 'Freshwater porpoise endemic to China.'),
        ('Forest Elephant', 'Loxodonta cyclotis', 'Critically Endangered', 'Central Africa', 'Smaller, forest-dwelling African elephant.'),
        ('Bonobo', 'Pan paniscus', 'Endangered', 'Congo Basin', 'Great ape closely related to the chimpanzee.'),
        ('Okapi', 'Okapia johnstoni', 'Endangered', 'Democratic Republic of the Congo', 'Forest giraffid with zebra-like legs.'),
        ('Sumatran Tiger', 'Panthera tigris sumatrae', 'Critically Endangered', 'Sumatra', 'Smallest surviving tiger subspecies.'),
        ('Bornean Orangutan', 'Pongo pygmaeus', 'Critically Endangered', 'Borneo', 'Great ape native to Borneo.'),
        ('Green Sea Turtle', 'Chelonia mydas', 'Endangered', 'Tropical and subtropical seas', 'Large sea turtle with smooth shell.'),
        ('African Wild Dog', 'Lycaon pictus', 'Endangered', 'Sub-Saharan Africa', 'Highly social and cooperative hunter.'),
        ('Golden Lion Tamarin', 'Leontopithecus rosalia', 'Endangered', 'Brazil', 'Small, brightly colored monkey.'),
        ('Hooded Grebe', 'Podiceps gallardoi', 'Critically Endangered', 'Patagonia', 'Rare diving bird of South America.'),
        ('Philippine Eagle', 'Pithecophaga jefferyi', 'Critically Endangered', 'Philippines', 'One of the world’s largest eagles.'),
        ('Northern White Rhino', 'Ceratotherium simum cottoni', 'Critically Endangered', 'Kenya', 'Only two known individuals remain.'),
        ('Sumatran Rhino', 'Dicerorhinus sumatrensis', 'Critically Endangered', 'Sumatra, Borneo', 'Smallest and hairiest rhino.'),
        ('Scimitar-horned Oryx', 'Oryx dammah', 'Extinct in the Wild', 'Sahara Desert', 'Antelope reintroduced in reserves.'),
        ('Madagascar Pochard', 'Aythya innotata', 'Critically Endangered', 'Madagascar', 'World’s rarest duck.'),
        ('Pygmy Three-toed Sloth', 'Bradypus pygmaeus', 'Critically Endangered', 'Isla Escudo de Veraguas', 'Smallest and rarest sloth.'),
        ('Black Rhino', 'Diceros bicornis', 'Critically Endangered', 'Southern Africa', 'One of two African rhino species.'),
        ('Hawksbill Sea Turtle', 'Eretmochelys imbricata', 'Critically Endangered', 'Tropical Oceans', 'Sea turtle prized for its shell.'),
        ('Leatherback Turtle', 'Dermochelys coriacea', 'Vulnerable', 'Global Oceans', 'Largest of all living turtles.'),
        ('Indus River Dolphin', 'Platanista gangetica minor', 'Endangered', 'Indus River', 'Freshwater dolphin endemic to Pakistan.'),
        ('Markhor', 'Capra falconeri', 'Near Threatened', 'Central Asia', 'Large wild goat with twisted horns.'),
        ('Przewalski’s Horse', 'Equus ferus przewalskii', 'Endangered', 'Mongolia', 'Last wild horse species.'),
        ('Saiga Antelope', 'Saiga tatarica', 'Critically Endangered', 'Central Asia', 'Antelope with distinctive nose.'),
        ('Ring-tailed Lemur', 'Lemur catta', 'Endangered', 'Madagascar', 'Easily recognized by its striped tail.'),
        ('Red Wolf', 'Canis rufus', 'Critically Endangered', 'Southeastern United States', 'Rare North American canid.'),
        ('Andean Condor', 'Vultur gryphus', 'Vulnerable', 'South America', 'World’s largest flying bird.'),
        ('Galápagos Penguin', 'Spheniscus mendiculus', 'Endangered', 'Galápagos Islands', 'Only penguin found north of the equator.'),
        ('Gooty Tarantula', 'Poecilotheria metallica', 'Critically Endangered', 'India', 'Striking blue tarantula.'),
        ('Fossa', 'Cryptoprocta ferox', 'Vulnerable', 'Madagascar', 'Largest carnivorous mammal in Madagascar.'),
        ('Tasmanian Devil', 'Sarcophilus harrisii', 'Endangered', 'Tasmania', 'World’s largest carnivorous marsupial.'),
    ]
    c.executemany('INSERT INTO animals (name, species, status, location, description) VALUES (?, ?, ?, ?, ?)', animals)
    conn.commit()
    conn.close()

def create_protected_areas_db(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS protected_areas (
        id INTEGER PRIMARY KEY,
        name TEXT,
        country TEXT,
        type TEXT,
        area_km2 REAL,
        description TEXT
    )''')
    parks = [
        ('Retezat National Park', 'Romania', 'National Park', 380.5, 'First national park in Romania, home to many endemic species.'),
        ('Bialowieza Forest', 'Poland', 'World Heritage Site', 1500, 'Ancient forest straddling the border of Poland and Belarus.'),
        ('Yellowstone National Park', 'USA', 'National Park', 8983, 'First national park in the world, famous for geysers.'),
        ('Kruger National Park', 'South Africa', 'National Park', 19485, 'One of Africa’s largest game reserves.'),
        ('Virunga National Park', 'DR Congo', 'National Park', 7800, 'Africa’s oldest national park, gorilla habitat.'),
        ('Banff National Park', 'Canada', 'National Park', 6641, 'Canada’s oldest national park, Rocky Mountains.'),
        ('Ujung Kulon National Park', 'Indonesia', 'National Park', 1220, 'Last refuge of the Javan Rhino.'),
        ('Serengeti National Park', 'Tanzania', 'National Park', 14763, 'Famous for its annual migration of wildebeest.'),
        ('Galápagos National Park', 'Ecuador', 'National Park', 7995, 'Unique flora and fauna, Darwin’s studies.'),
        ('Great Barrier Reef Marine Park', 'Australia', 'Marine Park', 344400, 'World’s largest coral reef system.'),
        ('Plitvice Lakes National Park', 'Croatia', 'National Park', 296, 'Known for cascading lakes and waterfalls.'),
        ('Chitwan National Park', 'Nepal', 'National Park', 932, 'Home to rhinos, tigers, and elephants.'),
        ('Komodo National Park', 'Indonesia', 'National Park', 1733, 'Home of the Komodo dragon.'),
        ('Sagarmatha National Park', 'Nepal', 'National Park', 1148, 'Contains Mount Everest.'),
        ('Cairngorms National Park', 'UK', 'National Park', 4528, 'Largest national park in the UK.'),
        ('Bwindi Impenetrable Forest', 'Uganda', 'National Park', 331, 'Famous for mountain gorillas.'),
        ('Doñana National Park', 'Spain', 'National Park', 543, 'Important wetland for migratory birds.'),
        ('Fiordland National Park', 'New Zealand', 'National Park', 12500, 'Largest of New Zealand’s national parks.'),
        ('Manú National Park', 'Peru', 'National Park', 17162, 'Biodiversity hotspot in the Amazon.'),
        ('Yosemite National Park', 'USA', 'National Park', 3027, 'Known for granite cliffs and waterfalls.'),
        ('Tsingy de Bemaraha', 'Madagascar', 'World Heritage Site', 1520, 'Limestone karst landscape and unique wildlife.'),
        ('Kaziranga National Park', 'India', 'National Park', 430, 'Home to the largest population of Indian rhinos.'),
        ('Zion National Park', 'USA', 'National Park', 595, 'Known for steep red cliffs.'),
        ('Sundarbans National Park', 'India', 'National Park', 1330, 'Largest mangrove forest, Bengal tiger habitat.'),
        ('Etosha National Park', 'Namibia', 'National Park', 22270, 'Salt pan and abundant wildlife.'),
    ]
    c.executemany('INSERT INTO protected_areas (name, country, type, area_km2, description) VALUES (?, ?, ?, ?, ?)', parks)
    conn.commit()
    conn.close()

def create_diets_db(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS diets (
        id INTEGER PRIMARY KEY,
        animal TEXT,
        diet TEXT,
        main_foods TEXT,
        notes TEXT
    )''')
    diets = [
        ('Lynx', 'Carnivore', 'Deer, hares, birds', 'Prefers roe deer and hares.'),
        ('European Bison', 'Herbivore', 'Grasses, bark, leaves', 'Feeds on more than 60 plant species.'),
        ('Amur Leopard', 'Carnivore', 'Roe deer, hares, badgers', 'Hunts at night.'),
        ('Mountain Gorilla', 'Herbivore', 'Leaves, shoots, fruit', 'Occasionally eats insects.'),
        ('Red Panda', 'Omnivore', 'Bamboo, berries, eggs', 'Mainly bamboo but also small animals.'),
        ('Snow Leopard', 'Carnivore', 'Wild sheep, goats, marmots', 'Ambush predator.'),
        ('Saola', 'Herbivore', 'Leaves, fruit, seeds', 'Very little is known about diet.'),
        ('Javan Rhino', 'Herbivore', 'Shoots, twigs, fallen fruit', 'Feeds in dense lowland rainforest.'),
        ('Sumatran Orangutan', 'Omnivore', 'Fruit, leaves, insects', 'Mostly fruit, but also honey and eggs.'),
        ('Hawksbill Turtle', 'Omnivore', 'Sponges, sea anemones, jellyfish', 'Important reef species.'),
        ('Vaquita', 'Carnivore', 'Fish, squid, crustaceans', 'Feeds in shallow waters.'),
        ('Black-footed Ferret', 'Carnivore', 'Prairie dogs', 'Almost exclusively prairie dogs.'),
        ('Iberian Lynx', 'Carnivore', 'Rabbits, birds', 'Rabbits make up 80% of diet.'),
        ('Giant Panda', 'Herbivore', 'Bamboo', 'Occasionally eats small rodents.'),
        ('Addax', 'Herbivore', 'Grasses, leaves', 'Can survive without water for long periods.'),
        ('Blue Whale', 'Carnivore', 'Krill', 'Consumes up to 4 tons of krill a day.'),
        ('Gharial', 'Carnivore', 'Fish', 'Long snout adapted for catching fish.'),
        ('Asian Elephant', 'Herbivore', 'Grass, fruit, bark', 'Eats up to 150kg of food per day.'),
        ('Siberian Tiger', 'Carnivore', 'Wild boar, deer, elk', 'Top predator in its habitat.'),
        ('Grevy’s Zebra', 'Herbivore', 'Grasses', 'Needs access to water daily.'),
        ('Northern Bald Ibis', 'Omnivore', 'Insects, lizards, seeds', 'Feeds in open areas.'),
        ('Kakapo', 'Herbivore', 'Seeds, fruit, pollen', 'Nocturnal and flightless.'),
        ('Hainan Gibbon', 'Omnivore', 'Fruit, leaves, insects', 'Highly frugivorous.'),
        ('Yangtze Finless Porpoise', 'Carnivore', 'Fish, shrimp', 'Freshwater diet.'),
        ('Forest Elephant', 'Herbivore', 'Fruit, bark, leaves', 'Key seed dispersers.'),
        ('Bonobo', 'Omnivore', 'Fruit, leaves, small animals', 'Shares food within group.'),
        ('Okapi', 'Herbivore', 'Leaves, buds, fungi', 'Browses in dense forest.'),
        ('Sumatran Tiger', 'Carnivore', 'Deer, wild boar', 'Ambush hunter.'),
        ('Bornean Orangutan', 'Omnivore', 'Fruit, insects, honey', 'Uses tools to extract insects.'),
        ('Green Sea Turtle', 'Herbivore', 'Seagrasses, algae', 'Juveniles are omnivorous.'),
        ('African Wild Dog', 'Carnivore', 'Antelope, rodents, birds', 'Hunts in packs.'),
        ('Golden Lion Tamarin', 'Omnivore', 'Fruit, insects, small vertebrates', 'Feeds in upper forest canopy.'),
        ('Hooded Grebe', 'Omnivore', 'Aquatic insects, crustaceans', 'Feeds in shallow lakes.'),
        ('Philippine Eagle', 'Carnivore', 'Monkeys, birds, reptiles', 'Apex predator in its range.'),
        ('Northern White Rhino', 'Herbivore', 'Grass', 'Grazes on short grasses.'),
        ('Sumatran Rhino', 'Herbivore', 'Leaves, twigs, fruit', 'Browses in dense forest.'),
        ('Scimitar-horned Oryx', 'Herbivore', 'Grasses, herbs', 'Survives in arid desert.'),
        ('Madagascar Pochard', 'Omnivore', 'Aquatic plants, insects', 'Feeds by diving.'),
        ('Pygmy Three-toed Sloth', 'Herbivore', 'Leaves', 'Restricted to mangrove forests.'),
        ('Black Rhino', 'Herbivore', 'Leaves, shoots, branches', 'Browses on woody plants.'),
        ('Hawksbill Sea Turtle', 'Omnivore', 'Sponges, jellyfish', 'Feeds on coral reefs.'),
        ('Leatherback Turtle', 'Carnivore', 'Jellyfish', 'Largest sea turtle.'),
        ('Indus River Dolphin', 'Carnivore', 'Fish, crustaceans', 'Echolocation specialist.'),
        ('Markhor', 'Herbivore', 'Grasses, leaves', 'Mountain goat.'),
        ('Przewalski’s Horse', 'Herbivore', 'Grasses', 'Last wild horse.'),
        ('Saiga Antelope', 'Herbivore', 'Grasses, herbs', 'Migratory steppe grazer.'),
        ('Ring-tailed Lemur', 'Omnivore', 'Fruit, leaves, flowers', 'Eats a wide variety of plants.'),
        ('Red Wolf', 'Carnivore', 'Deer, rodents, rabbits', 'Critically endangered canid.'),
        ('Andean Condor', 'Carnivore', 'Carrion', 'Largest flying bird.'),
        ('Galápagos Penguin', 'Carnivore', 'Fish, crustaceans', 'Feeds in cold upwelling waters.'),
        ('Gooty Tarantula', 'Carnivore', 'Insects', 'Arboreal tarantula.'),
        ('Fossa', 'Carnivore', 'Lemurs, rodents', 'Top predator in Madagascar.'),
        ('Tasmanian Devil', 'Carnivore', 'Carrion, small mammals', 'Largest carnivorous marsupial.'),
    ]
    c.executemany('INSERT INTO diets (animal, diet, main_foods, notes) VALUES (?, ?, ?, ?)', diets)
    conn.commit()
    conn.close()

# Create DBs
create_animals_db(os.path.join(FS_ROOT, 'home/admin/research/animals.db'))
create_protected_areas_db(os.path.join(FS_ROOT, 'home/admin/research/protected_areas.db'))
create_diets_db(os.path.join(FS_ROOT, 'home/admin/research/diets.db'))

# Create README and notes
with open(os.path.join(FS_ROOT, 'home/admin/research/README.md'), 'w') as f:
    f.write("""# Endangered Species Research

This directory contains research data on endangered animals, protected areas, and animal diets.
""")

with open(os.path.join(FS_ROOT, 'home/admin/research/notes.txt'), 'w') as f:
    f.write("Meeting with park rangers on Friday. Update animal database after field survey.\n")

with open(os.path.join(FS_ROOT, 'home/admin/scripts/query_animals.py'), 'w') as f:
    f.write("""#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect('../research/animals.db')
c = conn.cursor()
for row in c.execute('SELECT * FROM animals'):
    print(row)
conn.close()
""")

with open(os.path.join(FS_ROOT, 'home/admin/scripts/export_reports.sh'), 'w') as f:
    f.write("""#!/bin/bash
sqlite3 ../research/animals.db \".headers on\" \".mode csv\" \"SELECT * FROM animals;\" > ../../data/exports/animal_reports_2025.csv
""")

with open(os.path.join(FS_ROOT, 'home/admin/.bashrc'), 'w') as f:
    f.write("# .bashrc for admin\n")

os.makedirs(os.path.join(FS_ROOT, 'root'), exist_ok=True)
# with open(os.path.join(FS_ROOT, 'root/admin_notes.txt'), 'w') as f:
#     f.write("""
# TODO: Review animal tracking data.
# TODO: Update protected areas database after new satellite imagery.
# TODO: Prepare quarterly report for conservation board.
# TODO: Schedule meeting with field researchers next week.
# TODO: Check backup of SQLite databases.
# TODO: Verify data integrity of animal GPS tags.
# TODO: Respond to email from Dr. Smith regarding wolf population study.
# TODO: Organize files for upcoming grant submission.
# TODO: Archive last year's fieldwork photos.
# TODO: Double-check coordinates for lynx sightings in Romania.
# TODO: Update documentation for new research assistants.
# TODO: Cross-reference animal diet data with latest field reports.
#
# # Українські нотатки адміністратора
# TODO: Оновити дані про популяцію рисі у Карпатах.
# TODO: Перевірити звіти з національного парку "Шацький".
# TODO: Підготувати презентацію для екологічної конференції.
# TODO: Зв'язатися з місцевими волонтерами щодо моніторингу вовків.
# """)

# Create exported CSVs (placeholder content)
with open(os.path.join(FS_ROOT, 'data/exports/animal_reports_2025.csv'), 'w') as f:
    f.write("id,name,species,status,location\n1,Lynx,Lynx lynx,Endangered,Carpathian Mountains\n2,European Bison,Bison bonasus,Vulnerable,Bialowieza Forest\n")

with open(os.path.join(FS_ROOT, 'data/exports/protected_areas_list.csv'), 'w') as f:
    f.write("id,name,country,type\n1,Retezat National Park,Romania,National Park\n2,Bialowieza Forest,Poland,World Heritage Site\n")

# Create honeypot log file
with open(os.path.join(FS_ROOT, 'var/log/honeypot.log'), 'w') as f:
    f.write("[2025-06-18 14:30] Honeypot started.\n")

# Create plausible system files
with open(os.path.join(FS_ROOT, 'etc/passwd'), 'w') as f:
    f.write("root:x:0:0:root:/root:/bin/bash\nadmin:x:1000:1000:Admin User:/home/admin:/bin/bash\n")

with open(os.path.join(FS_ROOT, 'etc/hosts'), 'w') as f:
    f.write("127.0.0.1   localhost\n")


