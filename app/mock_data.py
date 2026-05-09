"""Mock data with ground truth for evaluation.

Design:
- 15 matched pairs (parent ↔ child) with varying difficulty
- 8 distractor parents (no matching child)
- 8 distractor children (no matching parent)
- Total: 23 parents + 23 children = 46 entries
- Child memories include realistic errors at 3 difficulty levels:
  - EASY (pairs 1-5): minor errors, strong physical feature overlap
  - MEDIUM (pairs 6-10): some wrong details, partial feature match
  - HARD (pairs 11-15): major distortions, fabricated memories, minimal overlap
"""

from app.models import Entry

# Ground truth: maps parent index (0-based) to child index (0-based)
# e.g. GROUND_TRUTH[0] = 0 means PARENT_ENTRIES[0] matches CHILD_ENTRIES[0]
GROUND_TRUTH = {i: i for i in range(15)}  # pairs 0-14 match 1:1

# Difficulty labels for analysis
PAIR_DIFFICULTY = {
    0: "easy", 1: "easy", 2: "easy", 3: "easy", 4: "easy",
    5: "medium", 6: "medium", 7: "medium", 8: "medium", 9: "medium",
    10: "hard", 11: "hard", 12: "hard", 13: "hard", 14: "hard",
}

# ============================================================
# PARENTS SEEKING CHILDREN
# ============================================================
PARENT_ENTRIES = [
    # --- EASY PAIRS (0-4): clear features, minor child memory errors ---

    # Pair 0: Emma
    Entry(
        entry_type="parent_seeking",
        name="Emma Chen",
        gender="female",
        birth_date="2006-03",
        missing_date="2011-07-14",
        location="Maple Harbor - Hillside District",
        physical_features="Heart-shaped birthmark on left shoulder blade; small scar above right eyebrow from a fall at age 2",
        description="Emma went missing on July 14, 2011 near Maple Hill Park. She was 5 years old, wearing a yellow sundress. She loved singing and could hum several Disney songs. She was bilingual in English and Mandarin. Her favorite toy was a stuffed elephant named 'Ellie'. Father is a software engineer, mother runs a bakery on Elmwood Street.",
        contact="David Chen 415-***-1234",
    ),
    # Pair 1: Marcus
    Entry(
        entry_type="parent_seeking",
        name="Marcus Johnson",
        gender="male",
        birth_date="2004-11",
        missing_date="2009-08-22",
        location="Ironwood - South End, near the university",
        physical_features="Large port-wine stain birthmark on right calf; missing tip of left pinky finger (accident with door at age 3)",
        description="Marcus disappeared from a playground near the university campus. He was almost 5, tall for his age. He loved trains and could name every elevated line. His grandmother raised him mostly, she called him 'Little Bear'. Father was a jazz musician who played saxophone at local clubs. Marcus had a slight stutter when excited.",
        contact="Angela Johnson 773-***-5678",
    ),
    # Pair 2: Sofia
    Entry(
        entry_type="parent_seeking",
        name="Sofia Reyes",
        gender="female",
        birth_date="2007-06",
        missing_date="2012-03-10",
        location="Sunfield - near the Galleria district",
        physical_features="Café-au-lait spot on left hip about 3cm; extra toe on right foot (polydactyly, surgically removed at 2 but scar remains)",
        description="Sofia vanished from a shopping mall food court. She was 4, wearing pink overalls. Very shy, rarely spoke to strangers. She had an older brother named Diego (8 at the time). Family spoke Spanish at home. Mother worked as a hotel housekeeper. Sofia was terrified of dogs but loved cats. She had a special blanket she carried everywhere, blue with white stars.",
        contact="Maria Reyes 832-***-9012",
    ),
    # Pair 3: Aiden
    Entry(
        entry_type="parent_seeking",
        name="Aiden O'Brien",
        gender="male",
        birth_date="2005-01",
        missing_date="2010-06-05",
        location="Harborton - Bayshore neighborhood",
        physical_features="Triangular scar on chin from dog bite; two prominent front teeth with a gap between them",
        description="Aiden went missing from his front yard on a Saturday afternoon. He was 5, red-haired with freckles. He was obsessed with fire trucks and wanted to be a firefighter. There was a fire station two blocks from the house and the firefighters knew him by name. His dad was a plumber. Aiden could already write his full name. He had a goldfish named 'Bubbles'.",
        contact="Sean O'Brien 617-***-3456",
    ),
    # Pair 4: Lily
    Entry(
        entry_type="parent_seeking",
        name="Lily Zhang",
        gender="female",
        birth_date="2008-09",
        missing_date="2013-04-18",
        location="Cedarvale - Heritage District",
        physical_features="Strawberry hemangioma on back of neck (raised red spot, about 1cm); webbed toes on left foot (2nd and 3rd toes)",
        description="Lily disappeared near Dragon Gate Park. She was 4.5 years old. Very energetic, loved to draw and always had crayons with her. Family owned a dim sum restaurant. She could speak Cantonese phrases. Grandmother called her 'Little Fish'. House was above the restaurant, she could always smell food cooking. Loved watching the ferries from the waterfront.",
        contact="Wei Zhang 206-***-7890",
    ),

    # --- MEDIUM PAIRS (5-9): child has more memory errors ---

    # Pair 5: Noah
    Entry(
        entry_type="parent_seeking",
        name="Noah Williams",
        gender="male",
        birth_date="2003-08",
        missing_date="2008-12-20",
        location="Pinecrest - Hilltop area",
        physical_features="Surgical scar on lower back (spinal surgery at age 1); birthmark shaped like a comma behind right ear",
        description="Noah was taken from outside a grocery store. He was 5, wearing a green winter coat. He was very quiet and liked to read picture books for hours. Father was a carpenter who built furniture in the garage workshop. Mother taught piano lessons at home. Noah was learning piano and could play 'Mary Had a Little Lamb'. Their cat was named 'Snowball', a white Persian. They lived in a Victorian house with a red front door.",
        contact="Robert Williams 303-***-2345",
    ),
    # Pair 6: Zara
    Entry(
        entry_type="parent_seeking",
        name="Zara Patel",
        gender="female",
        birth_date="2006-04",
        missing_date="2011-09-08",
        location="Willowbrook - Brookside area",
        physical_features="Vitiligo patch on right hand (white skin patch about 4cm); double-jointed thumbs",
        description="Zara went missing from her preschool parking lot. She was 5. Her parents owned an Indian restaurant. She loved to dance, especially Bollywood style. She was allergic to peanuts (carried an EpiPen). Her older sister Priya (age 8) taught her Hindi songs. The family had a German Shepherd named 'Raja'. They lived in a house with a big mango tree in the backyard.",
        contact="Raj Patel 404-***-6789",
    ),
    # Pair 7: Tyler
    Entry(
        entry_type="parent_seeking",
        name="Tyler Morrison",
        gender="male",
        birth_date="2005-12",
        missing_date="2010-05-30",
        location="Fernridge - near Fernridge Avenue District",
        physical_features="Burn scar on left forearm from pulling a pot of soup; right ear slightly deformed (microtia, smaller than left)",
        description="Tyler vanished from a community park during a neighborhood barbecue. He was 4.5. Very adventurous, always climbing things. His mom was a nurse who worked night shifts. His dad ran a used bookstore on Fernridge Avenue. Tyler loved dinosaurs, especially T-Rex, and had dozens of plastic dinosaur toys. He could already ride a bicycle without training wheels. The family lived above the bookstore.",
        contact="Janet Morrison 503-***-0123",
    ),
    # Pair 8: Chloe
    Entry(
        entry_type="parent_seeking",
        name="Chloe Kim",
        gender="female",
        birth_date="2007-02",
        missing_date="2011-11-15",
        location="Starlight City - the Korean quarter",
        physical_features="Mongolian spot (blue-gray mark) on lower back, larger than typical; small notch in left earlobe (from earring tear)",
        description="Chloe disappeared from outside a church. She was 4. She loved K-pop music even at that young age and would dance to it. Her grandmother (halmeoni) was her primary caretaker. Family ran a dry cleaning business. Chloe was a picky eater but loved kimchi jjigae. She had a pet turtle. Grandmother always braided her hair in two braids. The apartment was on the 3rd floor, near a busy intersection with a large neon sign outside.",
        contact="Jimin Kim 213-***-4567",
    ),
    # Pair 9: Lucas
    Entry(
        entry_type="parent_seeking",
        name="Lucas Rivera",
        gender="male",
        birth_date="2004-07",
        missing_date="2009-10-31",
        location="Redstone - near Red Canyon",
        physical_features="Prominent mole cluster on left shoulder (3-4 moles close together); scar on right knee from bicycle accident",
        description="Lucas went missing on Halloween night. He was dressed as a pirate. He was 5 years old. Father was a mechanic who always smelled like motor oil. Mother sold homemade tamales on weekends. Lucas loved playing in the desert and collecting rocks. He had an imaginary friend called 'Captain Rex'. The family had a rooster that woke everyone up at dawn. They lived near a canal where Lucas liked to watch the water flow.",
        contact="Carlos Rivera 602-***-8901",
    ),

    # --- HARD PAIRS (10-14): major child memory distortions ---

    # Pair 10: Maya
    Entry(
        entry_type="parent_seeking",
        name="Maya Cooper",
        gender="female",
        birth_date="2005-05",
        missing_date="2009-09-12",
        location="Melodia - East Melodia",
        physical_features="Heterochromia - right eye brown, left eye green; three parallel scars on left forearm from a cat scratch",
        description="Maya disappeared from a neighbor's yard. She was 4. Her father was a country music guitarist who performed at local bars. Mother was a tattoo artist. Maya was already showing artistic talent, drawing constantly. They lived in a colorful painted house - bright blue with yellow trim. A music studio was in the basement. Maya could play a few chords on ukulele. She had a cat named 'Hendrix'.",
        contact="Jake Cooper 615-***-2345",
    ),
    # Pair 11: Ethan
    Entry(
        entry_type="parent_seeking",
        name="Ethan Park",
        gender="male",
        birth_date="2006-10",
        missing_date="2011-03-22",
        location="Frostlake - Lakeside area",
        physical_features="Keloid scar on upper left arm from vaccination; sixth finger (surgically removed) left hand, small scar remains at base of pinky",
        description="Ethan went missing from a department store. He was 4.5. Family is Korean-American. Father owned a taekwondo studio. Mother worked at a bank. Ethan loved building with LEGO and was unusually good at it for his age. He was fascinated by snow and winter. The family had a Shih Tzu named 'Boba'. They lived in a condo near a lake. Ethan was afraid of fireworks.",
        contact="Daniel Park 612-***-6789",
    ),
    # Pair 12: Isabelle
    Entry(
        entry_type="parent_seeking",
        name="Isabelle Dubois",
        gender="female",
        birth_date="2004-03",
        missing_date="2008-08-04",
        location="Crescent Bay - Old Quarter area",
        physical_features="Port-wine stain birthmark on right temple extending to cheek; crooked right ring finger (healed fracture)",
        description="Isabelle vanished during a street festival. She was 4. Her family ran a Cajun restaurant. Father played trumpet in a brass band that practiced on weekends. Mother made pralines that they sold at the market. Isabelle loved water and swimming. They lived in a shotgun house with a courtyard that had a fountain. She spoke some French Creole phrases. She was scared of masks (common at festivals).",
        contact="Pierre Dubois 504-***-0123",
    ),
    # Pair 13: Jayden
    Entry(
        entry_type="parent_seeking",
        name="Jayden Brooks",
        gender="male",
        birth_date="2007-11",
        missing_date="2012-07-04",
        location="Steelhaven - Midtown",
        physical_features="Eczema patches on both inner elbows (chronic); strawberry birthmark on right buttock",
        description="Jayden disappeared during July 4th fireworks at the riverfront. He was 4.5. His mother was a hairdresser who worked from a home salon. His grandfather was a retired autoworker who took Jayden to car shows. Jayden was obsessed with cars, could identify makes and models. Very energetic, never sat still. He loved popsicles, especially grape flavor. They had a pit bull named 'Tank' who was very gentle with Jayden.",
        contact="Keisha Brooks 313-***-4567",
    ),
    # Pair 14: Olivia
    Entry(
        entry_type="parent_seeking",
        name="Olivia Santos",
        gender="female",
        birth_date="2005-08",
        missing_date="2010-02-14",
        location="Palmetto Shore - Little Havana district",
        physical_features="Dimple only on left cheek; nevus (large dark mole) on left ankle",
        description="Olivia went missing from outside a pharmacy on Valentine's Day. She was 4.5. Her great-grandmother lived with the family and told her stories in Spanish every night. Father ran a cigar shop. Mother was a dental hygienist. Olivia loved butterflies and had a collection of butterfly stickers. She would chase lizards in the yard. They had a parrot that could say her name. The house smelled like coffee and cigars. She attended a Catholic church and could recite prayers.",
        contact="Miguel Santos 305-***-8901",
    ),

    # --- DISTRACTOR PARENTS (15-22): no matching child ---

    Entry(
        entry_type="parent_seeking",
        name="Hannah Lee",
        gender="female",
        birth_date="2006-07",
        missing_date="2011-04-02",
        location="Oceanview - Hilltop",
        physical_features="Missing right canine tooth (knocked out); butterfly-shaped birthmark on right thigh",
        description="Hannah vanished from a park near the zoo. She was 4. She loved animals, especially elephants. Her parents were both teachers. She had a hamster named 'Peanut'. She was very talkative and friendly with strangers. She liked to wear her hair in pigtails.",
        contact="Jason Lee 619-***-1234",
    ),
    Entry(
        entry_type="parent_seeking",
        name="Ryan Mitchell",
        gender="male",
        birth_date="2003-05",
        missing_date="2008-09-15",
        location="Dockside - Harbor Row",
        physical_features="Cleft lip scar (surgically repaired); large freckle on left palm",
        description="Ryan disappeared from his school's aftercare program. He was 5. His father was a fisherman who worked on a crab boat. Ryan loved the ocean and could swim. He had a collection of seashells. Mother was a librarian. Ryan was afraid of the dark and slept with a nightlight shaped like a lighthouse.",
        contact="Tom Mitchell 215-***-5678",
    ),
    Entry(
        entry_type="parent_seeking",
        name="Amara Wilson",
        gender="female",
        birth_date="2008-01",
        missing_date="2012-06-20",
        location="Eastgate - Beacon Hill",
        physical_features="Sickle-shaped scar on left shin; unusually light iris in right eye compared to left",
        description="Amara went missing from a street fair. She was 4. Her mother was a gospel singer at the local church. Amara could already carry a tune. Father drove a delivery truck. She loved coloring books and would color for hours, always staying within the lines. She was very attached to her older brother James (age 7).",
        contact="Denise Wilson 410-***-9012",
    ),
    Entry(
        entry_type="parent_seeking",
        name="Kevin Nguyen",
        gender="male",
        birth_date="2005-09",
        missing_date="2010-01-10",
        location="Silicon Hills - near the Asian quarter",
        physical_features="Burn scar on right hand from touching a stove; flat nasal bridge with a small bump",
        description="Kevin disappeared from a Lunar New Year celebration. He was 4. His parents ran a pho restaurant. He loved noodles and would eat them every meal if allowed. He was very good with numbers and could count to 100 in both English and Vietnamese. He had a toy robot he took everywhere.",
        contact="Thanh Nguyen 408-***-3456",
    ),
    Entry(
        entry_type="parent_seeking",
        name="Stella Brown",
        gender="female",
        birth_date="2007-04",
        missing_date="2012-10-31",
        location="Wildflower - South River area",
        physical_features="Prominent bowed legs; small skin tag near left ear",
        description="Stella vanished on Halloween from a neighborhood trick-or-treat event. She was 5, dressed as a ladybug. Her father was a musician who played in a band at local venues. Mother made and sold jewelry. Stella loved music and could clap to any rhythm. She had a pet bearded dragon named 'Spike'.",
        contact="Brandon Brown 512-***-7890",
    ),
    Entry(
        entry_type="parent_seeking",
        name="Derek Chang",
        gender="male",
        birth_date="2004-02",
        missing_date="2009-05-25",
        location="Golden Meadow - River Park",
        physical_features="Deep dimples on both cheeks; raised circular mole on right forearm",
        description="Derek disappeared from a Memorial Day picnic at a park. He was 5. His mother was a nurse and his father was an accountant. Derek loved basketball and had a small hoop in the driveway. He could already dribble with both hands. He had a best friend named Tommy who lived next door.",
        contact="Linda Chang 916-***-0123",
    ),
    Entry(
        entry_type="parent_seeking",
        name="Nina Volkov",
        gender="female",
        birth_date="2006-11",
        missing_date="2011-08-08",
        location="Seaside Heights - Seaside Heights",
        physical_features="Strawberry birthmark behind right knee; slightly crossed right eye (strabismus)",
        description="Nina went missing from Seaside boardwalk. She was 4. Her family was Russian-speaking. Grandmother made borscht every Sunday. Father owned a small electronics repair shop. Nina loved the beach and building sandcastles. She was learning ballet. She had a favorite doll with a blue dress she called 'Masha'.",
        contact="Sergei Volkov 718-***-4567",
    ),
    Entry(
        entry_type="parent_seeking",
        name="Jerome Washington",
        gender="male",
        birth_date="2005-06",
        missing_date="2010-11-25",
        location="Archway - near the Archway Monument",
        physical_features="Keloid scar on right earlobe; webbing between right ring and middle fingers",
        description="Jerome disappeared from a Thanksgiving gathering at a relative's house. He was 5. His mother was a postal worker. His uncle was a barber who gave Jerome his haircuts. Jerome loved cartoons, especially superhero shows. He wanted to be a superhero when he grew up. He was very protective of his baby sister Maya (age 2).",
        contact="Patricia Washington 314-***-8901",
    ),
]

# ============================================================
# CHILDREN/ADULTS SEEKING FAMILY
# ============================================================
CHILD_ENTRIES = [
    # --- EASY (0-4): minor memory errors ---

    # Matches Pair 0 (Emma) - dog color slightly wrong, but features match well
    Entry(
        entry_type="child_seeking",
        name="(Current name: Amy Liu)",
        gender="female",
        birth_date="2006 (approx)",
        missing_date="Around 2011",
        location="Remember a hilly city with colorful houses and fog. Near a park with palm trees.",
        physical_features="Heart-shaped mark on my left shoulder area; scar above right eyebrow",
        description="I was about 5 when I came to my adoptive family. I remember singing a lot, maybe Disney songs. I think I spoke two languages. I had a stuffed animal - an elephant I think, I called it something with 'E'. I remember a woman baking - the smell of bread and cookies was always there. There was a man who worked on a computer all day. I think the bakery had a green sign out front (Note: actually no specific sign color mentioned).",
        contact="Amy Liu 510-***-2222",
    ),
    # Matches Pair 1 (Marcus) - remembers grandma, stuttering, train love
    Entry(
        entry_type="child_seeking",
        name="(Current name: Michael Brown)",
        gender="male",
        birth_date="2004-2005 (approx)",
        missing_date="Around 2009",
        location="Big city, very cold winters. Remember elevated trains and tall buildings.",
        physical_features="Big dark red birthmark on my right leg below the knee; left pinky finger is shorter than normal, tip seems missing",
        description="I was around 5 when I ended up with my adoptive family. My strongest memory is an old woman who called me 'Little Bear' - I think she was my grandma. She cooked amazing food. I remember the sound of trains overhead, and I could name different train lines. I remember a man playing some kind of horn instrument, the sound was beautiful. I used to s-s-stutter when I got excited about something.",
        contact="Michael Brown 312-***-3333",
    ),
    # Matches Pair 2 (Sofia) - remembers brother, fear of dogs, blanket
    Entry(
        entry_type="child_seeking",
        name="(Current name: Sophie Adams)",
        gender="female",
        birth_date="2007 (approx)",
        missing_date="Around 2012",
        location="Somewhere hot, a big city in the south. Remember a very large mall.",
        physical_features="Light brown spot on my left hip area; scar on right foot that looks like surgery was done there",
        description="I was about 4 when I arrived at my foster home. I remember an older boy, maybe a brother - his name started with 'D'. People at home spoke a language that wasn't English, maybe Spanish. I was absolutely terrified of dogs. I had a favorite blanket, blue with patterns on it - stars maybe? I remember a woman in a uniform, like a maid outfit. I loved cats. I was very quiet and didn't like talking to people I didn't know.",
        contact="Sophie Adams 713-***-4444",
    ),
    # Matches Pair 3 (Aiden) - remembers firefighters, red hair, gap teeth
    Entry(
        entry_type="child_seeking",
        name="(Current name: Andrew Foster)",
        gender="male",
        birth_date="2005 (approx)",
        missing_date="Around 2010",
        location="A city on the east coast, old buildings, near the ocean I think.",
        physical_features="Scar on my chin that looks like a triangle; I had a gap between my front teeth as a kid",
        description="I was around 5. I remember being obsessed with fire trucks. There were real firefighters nearby who knew me, they let me sit in the truck once. I had red hair and freckles - my adoptive family says I still had them when I arrived. My dad did something with pipes, he fixed things in houses. I could write my name already. I had a pet fish. I remember the yard where I was playing the last time I was at the old house.",
        contact="Andrew Foster 781-***-5555",
    ),
    # Matches Pair 4 (Lily) - remembers restaurant smells, drawing, grandma nickname
    Entry(
        entry_type="child_seeking",
        name="(Current name: Grace Wang)",
        gender="female",
        birth_date="2008-2009 (approx)",
        missing_date="Around 2013",
        location="Rainy city with water everywhere - boats, maybe ferries. Near a Chinatown area.",
        physical_features="Red raised bump on back of my neck; my toes on one foot are a bit stuck together",
        description="I was about 4 or 5. The strongest memory is the smell of food - steaming, savory food, all the time. I think we lived above a restaurant or very close to one. An old woman called me something like 'Little Fish' in another language. I always loved drawing, I carried crayons everywhere. I remember watching big boats on the water. I think I could speak some words in Chinese.",
        contact="Grace Wang 425-***-6666",
    ),

    # --- MEDIUM (5-9): more memory errors, some details wrong ---

    # Matches Pair 5 (Noah) - remembers dad building things but says "metal" instead of wood, piano correct
    Entry(
        entry_type="child_seeking",
        name="(Current name: Nathan Scott)",
        gender="male",
        birth_date="2003-2004 (approx)",
        missing_date="Around 2008-2009",
        location="Somewhere with mountains, cold, lots of snow in winter.",
        physical_features="Long scar on my lower back; some kind of mark behind my right ear, hard to see",
        description="I was about 5 when I moved to my adoptive home. I remember being very quiet, I liked looking at books with pictures. There was a man who built things - I remember the sound of hammering and sawing, maybe metalwork? (Note: actually woodwork/carpentry). There was music in the house, someone playing piano. We had a white cat (Note: actually a white Persian cat named Snowball). I remember a red door - our front door was red. It was a very cold place.",
        contact="Nathan Scott 720-***-7777",
    ),
    # Matches Pair 6 (Zara) - remembers dancing, restaurant, but says "Thai" instead of Indian
    Entry(
        entry_type="child_seeking",
        name="(Current name: Zoe Henderson)",
        gender="female",
        birth_date="2006 (approx)",
        missing_date="Around 2011",
        location="Warm city in the south, lots of trees. Remember a big parking lot.",
        physical_features="White patch of skin on my right hand; my thumbs bend backwards really far",
        description="About 5 when I was adopted. I remember spicy food everywhere, maybe a Thai restaurant? (Note: actually Indian). I loved to dance, fancy fast dancing with lots of hand movements. I had an older sister who sang songs in a foreign language. I remember a big dog, a shepherd type. There was a tree in the yard with some kind of tropical fruit. I'm allergic to peanuts, always have been. I remember the smell of curry and spices.",
        contact="Zoe Henderson 678-***-8888",
    ),
    # Matches Pair 7 (Tyler) - remembers bookstore, climbing, dinosaurs, but says mom ran the store
    Entry(
        entry_type="child_seeking",
        name="(Current name: Travis King)",
        gender="male",
        birth_date="2005-2006 (approx)",
        missing_date="Around 2010",
        location="Rainy city, lots of bridges. Remember a street with interesting shops.",
        physical_features="Burn mark on my left arm near the wrist; one of my ears is smaller than the other, the right one",
        description="I was around 4-5. I loved climbing everything, always getting in trouble for it. My mom ran a bookstore, I think (Note: actually dad ran it). We lived above or behind the store, surrounded by books. I was crazy about dinosaurs, had tons of toy dinosaurs. I could ride a bike already. I remember a barbecue party at a park where there were lots of people. Someone in my family worked at night, I remember them leaving when it was dark.",
        contact="Travis King 971-***-9999",
    ),
    # Matches Pair 8 (Chloe) - remembers grandma, Korean food, but says 5th floor instead of 3rd
    Entry(
        entry_type="child_seeking",
        name="(Current name: Claire Yang)",
        gender="female",
        birth_date="2007 (approx)",
        missing_date="Around 2011-2012",
        location="Big city, lots of Korean signs and shops. Very busy streets.",
        physical_features="Blue-gray spot on my lower back, pretty big; left earlobe has a small dent or notch",
        description="I was about 4. I remember an old woman taking care of me, she always braided my hair. There was music with Korean singing, I would dance to it. Something about a cleaning or laundry business. I was picky about food but there was one spicy soup I loved. We had some kind of pet in a tank, maybe a fish? (Note: actually a turtle). We lived high up, maybe 5th floor (Note: actually 3rd floor). There was a big bright sign outside the window at night.",
        contact="Claire Yang 562-***-1010",
    ),
    # Matches Pair 9 (Lucas) - remembers dad smelling like something, rock collecting, but Halloween details wrong
    Entry(
        entry_type="child_seeking",
        name="(Current name: Leo Martinez)",
        gender="male",
        birth_date="2004-2005 (approx)",
        missing_date="Around 2009",
        location="Very hot place, dry, like a desert. Mountains in the distance.",
        physical_features="Group of dark spots on my left shoulder; scar on my right knee",
        description="I was about 5. My dad always smelled like grease or oil, he worked with machines. I remember a woman making food wrapped in corn husks on weekends. I loved playing outside in the dirt, collecting interesting rocks and minerals. I had an imaginary friend whose name I can't quite remember, something like 'Captain' something. There was a bird, maybe a chicken, that was very loud in the mornings. I remember water flowing in a ditch or canal near the house. I think I went missing during some holiday, there were costumes involved - maybe a costume party? I was dressed as a cowboy (Note: actually dressed as a pirate).",
        contact="Leo Martinez 480-***-1111",
    ),

    # --- HARD (10-14): major distortions, fabricated memories ---

    # Matches Pair 10 (Maya) - eyes are correct, but many false memories mixed in
    Entry(
        entry_type="child_seeking",
        name="(Current name: Mia Thompson)",
        gender="female",
        birth_date="2005-2006 (approx)",
        missing_date="Around 2009-2010",
        location="Somewhere with a lot of music? Maybe the south? I'm really not sure.",
        physical_features="My eyes are different colors - one brown, one green; some scratches or scars on my left arm",
        description="I was maybe 4. My memories are really jumbled. I think there was music all the time, like a guitar maybe? Someone drew pictures, or maybe I did. I remember a brightly colored house - blue? And another color. I remember what might have been a basement where sounds came from. I think we had a pet, a dog or a cat, named after a musician? I'm not sure if I'm remembering real things or dreams. I think I played some kind of small guitar or similar instrument. Sometimes I remember a woman with colorful arms - tattoos maybe?",
        contact="Mia Thompson 629-***-1212",
    ),
    # Matches Pair 11 (Ethan) - remembers LEGO, snow, dog, but mixed with fabricated memories
    Entry(
        entry_type="child_seeking",
        name="(Current name: Eric Johnson)",
        gender="male",
        birth_date="2006-2007 (approx)",
        missing_date="Around 2011",
        location="Very cold place, lots of snow. Near some water, a lake maybe.",
        physical_features="Thick scar on my upper left arm; something weird about my left hand near the pinky, like a small bump or scar",
        description="I was around 4-5. I remember loving to build things with blocks, spending hours on it. I loved snow and cold weather. We had a small fluffy dog. I remember being scared of loud booming sounds, like thunder or explosions. Someone in my family did some kind of martial art or fighting sport, I remember a room with mats on the floor. I think we lived near a big body of water. I have this memory of a big department store where I got lost, but I'm not sure if that's real or something I saw on TV. I remember the dog was named after a drink - 'Coffee' or 'Cocoa' or something like that (Note: actually 'Boba').",
        contact="Eric Johnson 952-***-1313",
    ),
    # Matches Pair 12 (Isabelle) - remembers water, music, food smells, but massive location confusion
    Entry(
        entry_type="child_seeking",
        name="(Current name: Bella Richards)",
        gender="female",
        birth_date="2004-2005 (approx)",
        missing_date="Around 2008-2009",
        location="I think it was a coastal city? There was a lot of water. Very hot and humid. Maybe somewhere tropical? (Note: actually Crescent Bay)",
        physical_features="Dark red mark on my right face near the temple; one of my fingers on my right hand is crooked, the ring finger",
        description="I was around 4. Everything smells in my memory - sweet candy-like smell, cooking with lots of spices, something frying. There was always music, loud brass instruments, like a parade but not always a parade. I think my family had something to do with food, a restaurant maybe? I remember a house that was very long and narrow. There was water somewhere, a fountain? I remember being in a big crowd with scary faces, masks maybe, and I was crying. Someone played a loud horn instrument. I think I could say some words in another language, maybe French? I was scared of people in costumes.",
        contact="Bella Richards 786-***-1414",
    ),
    # Matches Pair 13 (Jayden) - remembers cars, grandpa, mom cutting hair, but thinks he was 3 not 4.5
    Entry(
        entry_type="child_seeking",
        name="(Current name: James Cooper)",
        gender="male",
        birth_date="2008 (approx, thinks younger than actual)",
        missing_date="Around 2011-2012, maybe summer",
        location="A big city, industrial feeling. Lots of empty buildings and parking lots.",
        physical_features="Itchy skin on the insides of my elbows, always has been; birthmark somewhere on my lower body, I'm told",
        description="I think I was around 3 when I was separated (Note: actually 4.5). I remember an old man taking me to see cars, big shiny cars lined up. I loved cars, I could tell them apart somehow. There was a woman who cut people's hair at our house, the smell of hair products. I was always running around, couldn't sit still. I loved frozen treats, one particular flavor - purple colored (grape). We had a strong, muscular dog who was actually super gentle. I remember loud booms and lights in the sky, and then nothing after that. I'm not even sure these memories are real.",
        contact="James Cooper 248-***-1515",
    ),
    # Matches Pair 14 (Olivia) - remembers lizards, parrot, coffee smell, but many details jumbled
    Entry(
        entry_type="child_seeking",
        name="(Current name: Lily Morgan)",
        gender="female",
        birth_date="2005-2006 (approx)",
        missing_date="Around 2010",
        location="Hot, tropical feeling. Palm trees. Bright colors everywhere. Latin music.",
        physical_features="Dimple on one side of my face only, the left; dark mole on my left ankle area",
        description="I was maybe 4 or 5. I remember chasing small green lizards in a yard. There was a bird that could talk - it said a name but I can't remember whose name. The house smelled like strong coffee all the time, and something smoky. There was a very old woman who told stories at bedtime in Spanish. I think someone in the family sold something from a small shop, tobacco or similar? I loved stickers, I collected something with stickers. I remember going to a big building with statues and candles, and learning words to repeat. I remember the day I went missing there were hearts everywhere - was it some holiday? A man bought me chocolate that day.",
        contact="Lily Morgan 954-***-1616",
    ),

    # --- DISTRACTOR CHILDREN (15-22): no matching parent ---

    Entry(
        entry_type="child_seeking",
        name="(Current name: Daniel Park)",
        gender="male",
        birth_date="2003-2005 (uncertain)",
        missing_date="Uncertain, maybe age 4-6",
        location="No clear memory, might have been a city",
        physical_features="Round birthmark on left shoulder",
        description="My memories are almost completely blank. I remember a woman holding me, probably my mother. I lived in a high building, I could see far from a balcony. I vaguely remember a very long car ride. That's all I have.",
        contact="Daniel Park 347-***-1717",
    ),
    Entry(
        entry_type="child_seeking",
        name="(Current name: Sarah Chen)",
        gender="female",
        birth_date="2006 (approx)",
        missing_date="Around 2010",
        location="Somewhere sunny and dry, maybe in the southwest",
        physical_features="Large burn scar on right leg from knee to mid-thigh; left ear has a small extra fold of skin",
        description="I was about 4. I remember a swimming pool and being in the water a lot. There were mountains that looked purple at sunset. I remember a woman singing to me in a language I don't understand now. I had a dog, a big brown dog. We lived in a house with a red tile roof. I remember cactus plants in the yard. Someone made cookies with chocolate chips almost every day.",
        contact="Sarah Chen 818-***-1818",
    ),
    Entry(
        entry_type="child_seeking",
        name="(Current name: Marcus Wright)",
        gender="male",
        birth_date="2005 (approx)",
        missing_date="Around 2009",
        location="Remember a castle-like building nearby, maybe a theme park?",
        physical_features="Scar through right eyebrow; both middle fingers are unusually short",
        description="I was around 4 when I came to my adoptive family. I remember a big castle with princesses - this might be from TV or a theme park, I honestly can't tell anymore. I remember a man putting me in a very large vehicle. Sweet cake. A white cat. My adoptive parents say I didn't remember anything when I arrived, so these might all be false memories I've constructed.",
        contact="Marcus Wright 407-***-1919",
    ),
    Entry(
        entry_type="child_seeking",
        name="(Current name: Jessica Kim)",
        gender="female",
        birth_date="2004-2006 (very uncertain)",
        missing_date="Uncertain",
        location="Remember the ocean and very high mountains - not sure if same place",
        physical_features="Dark red birthmark on back of neck; right hand ring finger nail grows in crooked",
        description="I don't know when I was separated from my family. I remember the ocean, hearing waves. I also remember snow-covered mountains. Maybe we moved? A woman with very long hair. A tall man whose face I can't picture. Heavy rain flooding a house. I don't know the order of these memories or if they're even real.",
        contact="Jessica Kim 808-***-2020",
    ),
    Entry(
        entry_type="child_seeking",
        name="(Current name: Tommy Lee)",
        gender="male",
        birth_date="2007 (approx)",
        missing_date="Around 2011",
        location="Don't remember the location at all",
        physical_features="Mole on left side of nose; long scar on right forearm",
        description="All I have are sensory memories. The smell of jasmine flowers. Someone singing a lullaby in a language I don't know. Burning wood smell. The sound of water, maybe a river. A blanket that smelled like sunshine. These fragments are all I have of my life before.",
        contact="Tommy Lee 469-***-2121",
    ),
    Entry(
        entry_type="child_seeking",
        name="(Current name: Anna Petrova)",
        gender="female",
        birth_date="2008-2009 (approx)",
        missing_date="Around 2010-2011",
        location="No memory at all",
        physical_features="Large café-au-lait birthmark on inner left thigh; tiny pit/hole near right ear (preauricular pit)",
        description="I was found at approximately age 2-3 so I have almost no memories. My adoptive parents say I was wearing a red coat and holding a yellow plastic duck. I learned to talk late. The only thing that might be a real memory is a recurring dream about a dark room that scares me.",
        contact="Anna Petrova 503-***-2222",
    ),
    Entry(
        entry_type="child_seeking",
        name="(Current name: Chris Williams)",
        gender="male",
        birth_date="2002-2003 (approx)",
        missing_date="Around 2006-2007",
        location="Remember living in at least three different places before my adoptive family",
        physical_features="Vertical scar above right eyebrow; dark ring-like mark around left wrist",
        description="Before my adoptive family, I was moved around. First place: rice paddies, rural farming area. Second place: a dirty dark room with several other kids. Third place: a kind woman bought me new clothes. Then my adoptive family in the Midwest. I don't have an accent so I can't tell where I'm originally from. I might have been trafficked through multiple hands.",
        contact="Chris Williams 614-***-2323",
    ),
    Entry(
        entry_type="child_seeking",
        name="(Current name: Maya Robinson)",
        gender="female",
        birth_date="2006 (approx)",
        missing_date="Around 2010",
        location="Somewhere with lots of rain and green trees",
        physical_features="Three small moles in a line on right collarbone; left knee has a patch of rough skin",
        description="I remember rain, lots of rain. Green everywhere. A house surrounded by trees. I remember a woman who smelled like flowers. She made soup in a big pot. There was music from a radio, old-fashioned sounding. A man with big hands who lifted me up high. I remember chickens in the yard. But I'm told I was found in a dry desert state far from here, which doesn't match any of these memories at all.",
        contact="Maya Robinson 775-***-2424",
    ),
]
