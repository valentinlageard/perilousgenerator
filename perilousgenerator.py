import collections
import random

class Die:
    '''Roll n times a die value (d4, d6, ...).'''
    def __init__(self, value, n=1):
        self.value = value
        self.n = n

    def roll(self):
        return sum(random.randint(1, self.value) for _ in range(self.n))

d2 = Die(2)
d3 = Die(3)
d4 = Die(4)
d6 = Die(6)
d8 = Die(8)
d10 = Die(10)
d12 = Die(12)
d20 = Die(20)
d100 = Die(100)

class Dice:
    '''Roll all die in dice_list and adds bonus.'''

    def __init__(self, dice_list, bonus=0):
        self.dice_list = dice_list
        self.bonus = bonus

    def roll(self):
        return sum(die.roll() for die in self.dice_list) + self.bonus

generators = {}

Entry = collections.namedtuple('Entry', ('min_result', 'outcomes'), defaults=(None,))

GenerateAction = collections.namedtuple('GenerateAction',
                                        ('generator_name', 'dice', 'repeat', 'associated'),
                                        defaults=(None, None, 1, True))

class Generator:
    def __init__(self, name, dice, entries=None, associated_generators=None):
        self.name = name
        self.dice = dice
        self.entries = entries
        self.associated_generators = associated_generators
        self._register()

    def _select_outcomes(self, result):
        previous_entry = self.entries[0]
        for entry in self.entries[1:]:
            if previous_entry.min_result <= result < entry.min_result:
                return previous_entry.outcomes
            else:
                previous_entry = entry
        return previous_entry.outcomes

    def _resolve(self, to_resolve, associated=True):
        if isinstance(to_resolve, GenerateAction):
            subgenerator = generators[to_resolve.generator_name]
            try:
                repeat = to_resolve.repeat.roll()
            except AttributeError:
                repeat = to_resolve.repeat
            if repeat > 1:
                return [subgenerator.generate(dice=to_resolve.dice, associated=associated)
                        for _ in range(repeat)]
            else:
                return subgenerator.generate(dice=to_resolve.dice, associated=associated)
        elif to_resolve in generators:
            return generators[to_resolve].generate()
        else:
            return [to_resolve]

    def generate(self, dice=None, associated=True):
        generated_texts = [self.name]
        if self.entries:
            result = self.dice.roll() if not dice else dice.roll()
            outcomes = self._select_outcomes(result)
            #print(outcomes)
            for outcome in outcomes:
                generated_texts.append(self._resolve(outcome, associated=associated))
        if associated:
            try:
                for generator in self.associated_generators:
                    generated_texts.append(self._resolve(generator, associated=associated))
            except TypeError:
                pass
        return generated_texts

    def _recursive_print(self, generated_texts, indent=None, is_last=True):
        if indent is None:
            indent = ''
        if isinstance(generated_texts[0], str):
            node_name = generated_texts[0]
            if is_last:
                print(indent + ' └─' + node_name)
                indent += '   '
            else:
                print(indent + ' ├─' + node_name)
                indent += ' │ '
            for i, generated_text in enumerate(generated_texts[1:]):
                self._recursive_print(generated_text, indent, (i == len(generated_texts[1:]) - 1))
        else:
            for i, generated_text in enumerate(generated_texts):
                self._recursive_print(generated_text, indent, False)

    def generate_print(self, depth=0):
        generated_texts = self.generate()
        #print(generated_texts)
        self._recursive_print(generated_texts)

    def _register(self):
        generators[self.name] = self


template = '''
Generator('', d12,
          (Entry(1, ('',)),
           Entry(2, ('',)),
           Entry(3, ('',)),
           Entry(4, ('',)),
           Entry(5, ('',)),
           Entry(6, ('',)),
           Entry(7, ('',)),
           Entry(8, ('',)),
           Entry(9, ('',)),
           Entry(10, ('',)),
           Entry(11, ('',)),
           Entry(12, ('',))),
          associated_generators=('',))
'''

# DISCOVERY ----------------------------------------------------------------------------------------

Generator('discovery', d12,
          (Entry(1, ('unnatural feature',
                     'How does it affect its surroundings ?')),
           Entry(2, ('natural feature',
                     'Describe how they notice it and what sets it appart ?')),
           Entry(5, ('evidence',
                     'Consider the implications and be ready for them to take the bait.')),
           Entry(7, ('creature',
                     'Not an immediate threat but might become one.')),
           Entry(9, ('structure',
                     'Who built it ? Is it connected to anything else they made nearby ?'))))

Generator('unnatural feature', d12,
          (Entry(1, ('unnatural feature arcane',)),
           Entry(10, ('unnatural feature planar',)),
           Entry(12, ('unnatural feature divine',))))

Generator('unnatural feature arcane', d12,
          (Entry(1, ('residue',)),
           Entry(3, ('blight',)),
           Entry(6, ('alteration/mutation',)),
           Entry(8, ('enchantment',)),
           Entry(11, ('source/repository',))),
          associated_generators=('alignement', 'magic type'))

Generator('unnatural feature planar', d12,
          (Entry(1, ('distortion/warp',)),
           Entry(5, ('portal/gate',)),
           Entry(9, ('rift/tear',)),
           Entry(11, ('outpost',))),
          associated_generators=('alignement', 'element'))

Generator('unnatural feature divine', d12,
          (Entry(1, ('mark/sign',)),
           Entry(4, ('cursed place',)),
           Entry(7, ('hallowed place',)),
           Entry(10, ('watched place',)),
           Entry(12, ('presence',))),
          associated_generators=('alignement', 'aspect'))

Generator('natural feature', d12,
          (Entry(1, ('lair',)),
           Entry(3, ('obstacle',)),
           Entry(5, ('terrain change',)),
           Entry(8, ('water feature',)),
           Entry(10, ('landmark',)),
           Entry(12, ('resource',))),
          )

Generator('lair', d12,
          (Entry(1, ('burrow',)),
           Entry(4, ('cave/tunnels',)),
           Entry(8, ('nest/aerie',)),
           Entry(10, ('hive',)),
           Entry(11, ('structure ruin',))),
          associated_generators=('visibility',
                                 'creature responsible',
                                 'creature'))

Generator('obstacle', d12,
          (Entry(1, ('difficult ground (specific to terrain)',)),
           Entry(6, ('cliff/crevasse/chasm',)),
           Entry(9, ('ravine/gorge',)),
           Entry(11, ('oddity',))))

Generator('terrain change', d12,
          (Entry(1, ('limited area of another terrain type',
                     'terrain')),
           Entry(5, ('crevice/hole/pit/cave',)),
           Entry(7, ('altitude change',)),
           Entry(9, ('canyon/valley',)),
           Entry(11, ('rise/peak in distance',))))

Generator('water feature', d12,
          (Entry(1, ('spring/hotspring',)),
           Entry(2, ('waterfall/geyser',)),
           Entry(3, ('creek/stream/brook',)),
           Entry(7, ('pond/lake',)),
           Entry(9, ('river',)),
           Entry(11, ('sea/ocean',))))

Generator('landmark', d12,
          (Entry(1, ('water-based (waterfall, geyser, ...)',)),
           Entry(4, ('plant-based (ancient tree, giant flowers, ...)',)),
           Entry(7, ('earth-based (peak, formation, crater, ...)',)),
           Entry(11, ('oddity',))))

Generator('resource', d12,
          (Entry(1, ('game/fruit/vegetable',)),
           Entry(5, ('herb/spice/dye source',)),
           Entry(7, ('timber/stone',)),
           Entry(10, ('ore (copper, iron, ...)',)),
           Entry(12, ('precious metal/gems',))),
          associated_generators=('size',
                                 'visibility'))

Generator('evidence', d12,
          (Entry(1, ('tracks/spoor',)),
           Entry(7, ('remains/debris',
                     'age',
                     'visibility')),
           Entry(11, ('stash/cache',))))

Generator('tracks/spoor', d12,
          (Entry(1, ('faint/unclear',)),
           Entry(4, ('definite/clear',)),
           Entry(7, ('multiple',)),
           Entry(9, ('signs of violence',)),
           Entry(11, ('trail of blood/other',))),
          associated_generators=('age',
                                 'creature responsible',
                                 'creature'))

Generator('remains/debris', d12,
          (Entry(1, ('bones',)),
           Entry(5, ('corpse/carcass',)),
           Entry(8, ('site of violence',)),
           Entry(10, ('junk/refuse',)),
           Entry(11, ('lost supplies/cargo',)),
           Entry(12, ('tools/weapons/armor',))))

Generator('stash/cache', d12,
          (Entry(1, ('trinkets/coins',)),
           Entry(4, ('tools/weapons/armor',)),
           Entry(6, ('map',)),
           Entry(8, ('food/supplies',)),
           Entry(10, ('treasure',))))

Generator('structure', d12,
          (Entry(1, ('structure enigmatic',)),
           Entry(2, ('structure infrastructure',)),
           Entry(4, ('structure dwelling',)),
           Entry(5, ('structure burial/religious',)),
           Entry(7, ('steading',)),
           Entry(9, ('structure ruin',))))

Generator('structure enigmatic', d12,
          (Entry(1, ('earthworks',)),
           Entry(5, ('megalith',)),
           Entry(9, ('statue/idol/totem',)),
           Entry(12, ('oddity',))),
          associated_generators=(GenerateAction('age',Dice([d8], 4)),
                                 GenerateAction('size',Dice([d8], 4)),
                                 'visibility'))

Generator('structure infrastructure', d12,
          (Entry(1, ('track/path',)),
           Entry(5, ('road',)),
           Entry(9, ('bridge/ford',)),
           Entry(11, ('mine/quarry',)),
           Entry(12, ('aqueduct/canal/portal',))),
          associated_generators=('creature responsible',
                                 GenerateAction('creature', Dice([d4],4)),))

Generator('structure dwelling', d12,
          (Entry(1, ('campsite',)),
           Entry(4, ('hovel/hut',)),
           Entry(7, ('farm',)),
           Entry(9, ('inn/roadhouse',)),
           Entry(11, ('tower/keep/estate',))),
          associated_generators=('creature responsible',
                                 GenerateAction('creature', Dice([d4],4)),))

Generator('structure burial/religious', d12,
          (Entry(1, ('grave marker/barrow',)),
           Entry(3, ('graveyard/necropolis',)),
           Entry(5, ('tomb/crypt',)),
           Entry(7, ('shrine',)),
           Entry(10, ('temple/retreat',)),
           Entry(12, ('great temple',))),
          associated_generators=('alignement',
                                 'aspect',
                                 'creature responsible',
                                 GenerateAction('creature', Dice([d4],+4))))

Generator('structure ruin', d12,
          (Entry(1, (GenerateAction('structure infrastructure', Dice([d6],+6), associated=False),)),
           Entry(3, (GenerateAction('structure dwelling', Dice([d8],+4), associated=False),)),
           Entry(5, (GenerateAction('structure burial/religious', Dice([d8],+4), associated=False),)),
           Entry(7, (GenerateAction('steading', Dice([d10],+2), associated=False),)),
           Entry(9, ('dungeon',))),
          associated_generators=(GenerateAction('age', Dice([d8],+4)),
                                 'ruination',
                                 'visibility'))

Generator('steading', d12,
          (Entry(1, ('village',)),
           Entry(6, ('town',)),
           Entry(9, ('keep',)),
           Entry(12, ('city',))))

# DUNGEON ------------------------------------------------------------------------------------------

Generator('dungeon', d12,
          (Entry(1, ('dungeon small',)),
           Entry(4, ('dungeon medium',)),
           Entry(10, ('dungeon large',)),
           Entry(12, ('dungeon huge',))))

Generator('dungeon small', d12,
          associated_generators=('dungeon function',
                                 'dungeon themes',
                                 GenerateAction('dungeon theme', repeat=d4),
                                 'areas (1d6+2)',
                                 'dungeon builder',
                                 'dungeon ruination'))

Generator('dungeon medium', d12,
          associated_generators=('dungeon function',
                                 'dungeon themes',
                                 GenerateAction('dungeon theme', repeat=d6),
                                 'areas (2d6+4)',
                                 'dungeon builder',
                                 'dungeon ruination'))

Generator('dungeon large', d12,
          associated_generators=('dungeon function',
                                 'dungeon themes',
                                 GenerateAction('dungeon theme', repeat=Dice([d6],1)),
                                 'areas (3d6+6)',
                                 'dungeon builder',
                                 'dungeon ruination'))

Generator('dungeon huge', d12,
          associated_generators=('dungeon function',
                                 'dungeon themes',
                                 GenerateAction('dungeon theme', repeat=Dice([d6],2)),
                                 'areas (4d6+10)',
                                 'dungeon builder',
                                 'dungeon ruination'))

Generator('dungeon function', d12,
          (Entry(1, ('source/portal',)),
           Entry(2, ('mine',)),
           Entry(3, ('tomb/crypt',)),
           Entry(5, ('prison',)),
           Entry(6, ('lair/den/hideout',)),
           Entry(8, ('stronghold/sanctuary',)),
           Entry(10, ('shrine/temple/oracle',)),
           Entry(11, ('archive/library',)),
           Entry(12, ('unknown/mystery',))))

Generator('dungeon theme', d12,
          (Entry(1, ('dungeon theme mundane',)),
           Entry(6, ('dungeon theme unusual',)),
           Entry(10, ('dungeon theme extroardinary',))))

Generator('dungeon theme mundane', d12,
          (Entry(1, ('rot/decay',)),
           Entry(2, ('torture/agony',)),
           Entry(3, ('madness',)),
           Entry(4, ('all is lost',)),
           Entry(5, ('noble sacrifice',)),
           Entry(6, ('savage fury',)),
           Entry(7, ('survival',)),
           Entry(8, ('criminal activity',)),
           Entry(9, ('secrets/treachery',)),
           Entry(10, ('tricks and traps',)),
           Entry(11, ('invasion/infestation',)),
           Entry(12, ('factions at war',))))

Generator('dungeon theme unusual', d12,
          (Entry(1, ('creation/invention',)),
           Entry(2, ('element',)),
           Entry(3, ('knowledge/learning',)),
           Entry(4, ('growth/expansion',)),
           Entry(5, ('deepening mystery',)),
           Entry(6, ('transformation/change',)),
           Entry(7, ('chaos and destruction',)),
           Entry(8, ('shadowy forces',)),
           Entry(9, ('forbidden knowledge',)),
           Entry(10, ('poison/disease',)),
           Entry(11, ('corruption/blight',)),
           Entry(12, ('impending disaster',))))

Generator('dungeon theme extroardinary', d12,
          (Entry(1, ('scheming evil',)),
           Entry(2, ('divination/scrying',)),
           Entry(3, ('blasphemy',)),
           Entry(4, ('arcane research',)),
           Entry(5, ('occult forces',)),
           Entry(6, ('an ancient curse',)),
           Entry(7, ('mutation',)),
           Entry(8, ('the unquiet dead',)),
           Entry(9, ('bottomless hunger',)),
           Entry(10, ('incredible power',)),
           Entry(11, ('unspeakable horrors',)),
           Entry(12, ('holy war',))))

Generator('dungeon ruination', d12,
          (Entry(1, ('arcane disaster',)),
           Entry(2, ('damnation/curse',)),
           Entry(3, ('earthquake/fire/flood',)),
           Entry(5, ('plague/famine/drought',)),
           Entry(7, ('overrun by monsters',)),
           Entry(9, ('war/invasion',)),
           Entry(11, ('depleted resources',)),
           Entry(12, ('better prospects elsewhere',))))

Generator('dungeon builder', d12,
          (Entry(1, ('aliens/precursors',)),
           Entry(2, ('demigod/demon',)),
           Entry(3, ('natural (caves, etc.)',)),
           Entry(5, ('religious order/cult',)),
           Entry(6, ('humanoid',)),
           Entry(8, ('dwarves/gnomes',)),
           Entry(10, ('elves',)),
           Entry(11, ('wizard/madman',)),
           Entry(12, ('monarch/warlord',))))

Generator('dungeon exploration', d12,
          (Entry(1, ('unthemed area, common, empty',)),
           Entry(2, ('unthemed area, common','dungeon danger')),
           Entry(3, ('unthemed area, common','dungeon discovery','dungeon danger')),
           Entry(5, ('unthemed area, common','dungeon discovery')),
           Entry(7, ('themed area, common','dungeon danger')),
           Entry(8, ('themed area, common','dungeon discovery','dungeon danger')),
           Entry(9, ('themed area, common','dungeon discovery')),
           Entry(10, ('themed area, unique','dungeon danger')),
           Entry(11, ('themed area, unique','dungeon discovery','dungeon danger')),
           Entry(12, ('themed area, unique','dungeon discovery'))))

Generator('dungeon discovery', d12,
          (Entry(1, ('dungeon discovery dressing',)),
           Entry(4, ('dungeon discovery feature',)),
           Entry(10, ('dungeon discovery find',))))

Generator('dungeon discovery dressing', d12,
          (Entry(1, ('junk/debris',)),
           Entry(2, ('tracks/marks',)),
           Entry(3, ('signs of battle',)),
           Entry(4, ('writing/carving',)),
           Entry(5, ('warning',)),
           Entry(6, ('dead creature',
                     'creature')),
           Entry(7, ('bones/remains',)),
           Entry(8, ('book/scroll/map',)),
           Entry(9, ('broken door/wall',)),
           Entry(10, ('breeze/wind/smell',)),
           Entry(11, ('lichen/moss/fungus',)),
           Entry(12, ('oddity',))))

Generator('dungeon discovery feature', d12,
          (Entry(1, ('cave-in/collapse',)),
           Entry(2, ('pit/shaft/chasm',)),
           Entry(3, ('pillars/columns',)),
           Entry(4, ('locked door/gate',)),
           Entry(5, ('alcoves/niches',)),
           Entry(6, ('bridge/stairs/ramp',)),
           Entry(7, ('fountain/well/pool',)),
           Entry(8, ('puzzle',)),
           Entry(9, ('altar/dais/platform',)),
           Entry(10, ('statue/idol',)),
           Entry(11, ('magic pool/statue/idol',)),
           Entry(12, ('connection to another dungeon',))))

Generator('dungeon discovery find', d12,
          (Entry(1, ('trinkets',)),
           Entry(2, ('tools',)),
           Entry(3, ('weapons/armor',)),
           Entry(4, ('supplies/trade goods',)),
           Entry(5, ('coins/gems/jewelry',)),
           Entry(6, ('poisons/potions',)),
           Entry(7, ('adventurer/captive',)),
           Entry(8, ('magic item',)),
           Entry(9, ('scroll/book',)),
           Entry(10, ('magic weapon/armor',)),
           Entry(11, ('artifact',)),
           Entry(12, ('dungeon discovery find','dungeon discovery find'))))

Generator('dungeon danger', d12,
          (Entry(1, ('dungeon danger trap',)),
           Entry(5, ('dungeon danger creature',)),
           Entry(12, ('dungeon danger entity',))))

Generator('dungeon danger trap', d12,
          (Entry(1, ('alarm',)),
           Entry(2, ('ensnaring/paralyzing',)),
           Entry(3, ('pit',)),
           Entry(4, ('crushing',)),
           Entry(5, ('piercing/puncturing',)),
           Entry(6, ('chopping/slashing',)),
           Entry(7, ('confusing (maze, etc.)',)),
           Entry(8, ('gaz (poison, etc.)',)),
           Entry(9, ('element',)),
           Entry(10, ('ambush',)),
           Entry(11, ('magical',)),
           Entry(12, ('dungeon danger trap','dungeon danger trap'))))

Generator('dungeon danger creature', d12,
          (Entry(1, ('waiting in ambush',)),
           Entry(2, ('fighting/squabbling',)),
           Entry(3, ('prowling/on patrol',)),
           Entry(4, ('looking for food',)),
           Entry(5, ('eating/resting',)),
           Entry(6, ('guarding',)),
           Entry(7, ('on the move',)),
           Entry(8, ('searching/scavenging',)),
           Entry(9, ('returning to den',)),
           Entry(10, ('making plans',)),
           Entry(11, ('sleeping',)),
           Entry(12, ('dying',))),
          associated_generators=('creature',))

Generator('dungeon danger entity', d12,
          (Entry(1, ('alien interloper',)),
           Entry(2, ('vermin lord',)),
           Entry(3, ('criminal mastermind',)),
           Entry(4, ('warlord',)),
           Entry(5, ('high priest',)),
           Entry(6, ('oracle',)),
           Entry(7, ('wizard/witch/alchemist',)),
           Entry(8, ('monster lord',
                     'monster')),
           Entry(9, ('evil spirit/ghost',)),
           Entry(10, ('undead lord (lich, etc.)',)),
           Entry(11, ('demon',)),
           Entry(12, ('dark god',))))

# DANGERS ------------------------------------------------------------------------------------------

Generator('danger', d12,
          (Entry(1, ('unnatural entity (describt it, creepy, twisted, awe-inspinring)',
                     'unnatural entity')),
           Entry(2, ('hazard (threaten them and their stuff)',
                     'hazard')),
           Entry(7, ('creature',))))

Generator('unnatural entity', d12,
          (Entry(1, ('unnatural entity undead',)),
           Entry(9, ('unnatural entity planar',)),
           Entry(12, ('unnatural entity divine',))))

Generator('unnatural entity undead', d12,
          (Entry(1, ('haunt/wisp',)),
           Entry(5, ('ghost/spectre',)),
           Entry(9, ('banshee',)),
           Entry(10, ('wraith/wight',)),
           Entry(12, ('spirit lord/master',))),
          associated_generators=('ability',
                                 'activity',
                                 'alignement',
                                 'disposition'))

Generator('unnatural entity planar', d12,
          (Entry(1, ('imp (Small)',)),
           Entry(4, ('lesser elemental',)),
           Entry(7, ('lesser demon/horror',)),
           Entry(10, ('greater elemental',)),
           Entry(11, ('greater demon/horror',)),
           Entry(12, ('devil/elemental lord',))),
          associated_generators=('ability',
                                 'activity',
                                 'alignement',
                                 'disposition',
                                 'element',
                                 'feature',
                                 'monster tag'))

Generator('unnatural entity divine', d12,
          (Entry(1, ('agent',)),
           Entry(6, ('champion',)),
           Entry(10, ('army (Horde)',)),
           Entry(12, ('avatar',))),
          associated_generators=('ability',
                                 'activity',
                                 'alignement',
                                 'disposition',
                                 'element',
                                 'feature',
                                 'monster tag'))

Generator('hazard', d12,
          (Entry(1, ('hazard unnatural',)),
           Entry(3, ('hazard natural',)),
           Entry(11, ('hazard trap',))))

Generator('hazard unnatural', d12,
          (Entry(1, ('taint/blight/curse',)),
           Entry(4, ('arcane trap/effect',)),
           Entry(9, ('planar trap/effect',)),
           Entry(12, ('divine',))),
          associated_generators=('aspect',
                                 'visibility'))

Generator('hazard natural', d12,
          (Entry(1, ('blinding mist/fog',)),
           Entry(3, ('bog/mire/quicksand',)),
           Entry(5, ('pitfall/sinkhole/chasm',)),
           Entry(8, ('poison/disease',)),
           Entry(10, ('flood/fire/tornado',)),
           Entry(12, ('oddity',))))

Generator('hazard trap', d12,
          (Entry(1, ('alarm',)),
           Entry(3, ('ensnaring/paralysing',)),
           Entry(6, ('injurious (pit, etc...)',)),
           Entry(9, ('gas/fire/poison',)),
           Entry(10, ('ambush',))),
          associated_generators=('aspect',
                                 'visibility',
                                 'creature responsible',
                                 'creature'))

# CREATURES ----------------------------------------------------------------------------------------

Generator('creature', d12,
          (Entry(1, ('beast',)),
           Entry(5, ('human',
                     'npc occupation',
                     'npc trait',
                     'activity',
                     'alignement',
                     'disposition',
                     'group number')),
           Entry(7, ('humanoid',)),
           Entry(9, ('monster',))))

Generator('beast', d12,
          (Entry(1, ('beast earthbound',)),
           Entry(8, ('beast airborne',)),
           Entry(11, ('beast water-going',))),
          associated_generators=('activity',
                                 'disposition',
                                 'group number',
                                 'size'))

Generator('beast earthbound', d12,
          (Entry(1, ('termite/tick/louse',)),
           Entry(2, ('snail/slug/worm',)),
           Entry(3, ('ant/centipede/scorpion',)),
           Entry(4, ('snake/lizard',)),
           Entry(5, ('vole/rat/weasel',)),
           Entry(6, ('boar/pig',)),
           Entry(7, ('dog/fox/wolf',)),
           Entry(8, ('cat/lion/panther',)),
           Entry(9, ('deer/horse/camel',)),
           Entry(10, ('ox/rhino',)),
           Entry(11, ('bear/ape/gorilla',)),
           Entry(12, ('mammoth/dinosaur',))))

Generator('beast airborne', d12,
          (Entry(1, ('mosquito/firefly',)),
           Entry(2, ('locust/dragonfly/moth',)),
           Entry(3, ('bee/wasp',)),
           Entry(4, ('chicken/duck/goose',)),
           Entry(5, ('songbird/parrot',)),
           Entry(6, ('gull/waterbird',)),
           Entry(7, ('heron/crane/stork',)),
           Entry(8, ('crow/raven',)),
           Entry(9, ('hawk/falcon',)),
           Entry(10, ('eagle/owl',)),
           Entry(11, ('condor',)),
           Entry(12, ('pteranodon',))))

Generator('beast water-going', d12,
          (Entry(1, ('insect',)),
           Entry(2, ('jelly/anemone',)),
           Entry(3, ('clam/oyster/snail',)),
           Entry(4, ('eel/snake',)),
           Entry(5, ('frog/toad',)),
           Entry(6, ('fish',)),
           Entry(7, ('crab/lobster',)),
           Entry(8, ('turtle',)),
           Entry(9, ('alligator/crocodile',)),
           Entry(10, ('dolphin/shark',)),
           Entry(11, ('squid/octopus',)),
           Entry(12, ('whale',))))

Generator('humanoid', d12,
          (Entry(1, ('humanoid common',)),
           Entry(8, ('humanoid uncommon',)),
           Entry(11, ('humanoid hybrid',))),
          associated_generators=('npc occupation',
                                 'npc trait',
                                 'activity',
                                 'disposition',
                                 'group number',
                                 'alignement'))

Generator('humanoid common', d12,
          (Entry(1, ('halfling (Small)',)),
           Entry(4, ('goblin/kobold (Small)',)),
           Entry(6, ('dwarf/gnome (Small)',)),
           Entry(8, ('orc/hobgobelin/gnoll',)),
           Entry(10, ('half-elf/half-orc/etc...',)),
           Entry(12, ('elf',))))

Generator('humanoid uncommon', d12,
          (Entry(1, ('fey (Tiny)',)),
           Entry(2, ('catfolk/dogfolk',)),
           Entry(4, ('lizardfolk/merfolk',)),
           Entry(7, ('birdfolk',)),
           Entry(8, ('ogre/troll (Large)',)),
           Entry(11, ('cyclops/giant (Large)',))))

Generator('humanoid hybrid', d12,
          (Entry(1, ('centaur',)),
           Entry(3, ('werewolf/werebear',)),
           Entry(6, ('werecreature: human + beast','beast')),
           Entry(7, ('human + beast','beast')),
           Entry(11, ('human + 2 beasts','beast','beast'))))

Generator('monster', d12,
          (Entry(1, ('monster unusual',)),
           Entry(8, ('monster rare',)),
           Entry(11, ('monster legendary',))),
          associated_generators=('activity',
                                 'disposition',
                                 'size',
                                 'alignement',
                                 'group number',
                                 'OPTIONAL',
                                 'ability',
                                 'adjective',
                                 'age',
                                 'aspect',
                                 'condition',
                                 'feature',
                                 'monster tag'))

Generator('monster unusual', d12,
          (Entry(1, ('plant/fungus',)),
           Entry(4, ('Undead Human',)),
           Entry(6, ('Undead humanoid','humanoid')),
           Entry(7, ('beast + beast','beast','beast')),
           Entry(9, ('beast + ability','beast','ability')),
           Entry(11, ('beast + feature','beast','feature'))))

Generator('monster rare', d12,
          (Entry(1, ('slime/ooze (Amorphous)',)),
           Entry(4, ('creation (Construct)',)),
           Entry(7, ('beast + oddity','beast','oddity')),
           Entry(10, ('unnatural entity',))))

Generator('monster legendary', d12,
          (Entry(1, ('dragon/colossus (Huge)',)),
           Entry(4, ('monster unusual + Huge','monster unusual')),
           Entry(7, ('monster rare + Huge','monster rare')),
           Entry(10, ('beast + dragon','beast')),
           Entry(11, ('monster unusual + dragon','monster unusual')),
           Entry(12, ('monster rare + dragon','monster rare'))))

# NPC

Generator('npc occupation', d12,
          (Entry(1, ('criminal',)),
           Entry(2, ('commoner',)),
           Entry(7, ('tradesperson',)),
           Entry(9, ('merchant',)),
           Entry(11, ('specialist',)),
           Entry(12, ('official',))))

Generator('criminal', d12,
          (Entry(1, ('bandit/brigand/thug',)),
           Entry(3, ('thief',)),
           Entry(5, ('bodyguard/tough',)),
           Entry(7, ('burglar',)),
           Entry(9, ('dealer/fence',)),
           Entry(10, ('racketeer',)),
           Entry(11, ('lieutenant',)),
           Entry(12, ('boss',))))

Generator('commoner', d12,
          (Entry(1, ('housewife/husband',)),
           Entry(2, ('hunter/gatherer',)),
           Entry(4, ('farmer/herder',)),
           Entry(7, ('laborer/servant',)),
           Entry(9, ('driver/porter/guide',)),
           Entry(10, ('sailor/soldier/guard',)),
           Entry(11, ('clergy/monk',)),
           Entry(12, ('apprentice/adventurer',))))

Generator('tradesperson', d12,
          (Entry(1, ('cobbler/furrier/tailor',)),
           Entry(2, ('weaver/basketmaker',)),
           Entry(3, ('potter/carpenter',)),
           Entry(4, ('mason/baker/chandler',)),
           Entry(5, ('cooper/wheelwright',)),
           Entry(6, ('tanner/ropemaker',)),
           Entry(7, ('smith/tinker',)),
           Entry(8, ('stablekeeper/herbalist',)),
           Entry(9, ('vintner/jeweler',)),
           Entry(10, ('inkeeper/tavernkeeper',)),
           Entry(11, ('artist/actor/minstrel',)),
           Entry(12, ('armorer/weaponsmith',))))

Generator('merchant', d12,
          (Entry(1, ('general goods/outfitter',)),
           Entry(4, ('raw materials',)),
           Entry(5, ('grain/livestock',)),
           Entry(6, ('ale/wine/spirits',)),
           Entry(7, ('clothing/jewelry',)),
           Entry(8, ('weapons/armor',)),
           Entry(9, ('spices/tobacco',)),
           Entry(10, ('labor/slaves',)),
           Entry(11, ('books/scrolls',)),
           Entry(12, ('magic supplies/items',))))

Generator('specialist', d12,
          (Entry(1, ('undertaker',)),
           Entry(2, ('sage/scholar/wizard',)),
           Entry(3, ('writer/illuminator',)),
           Entry(4, ('perfumer',)),
           Entry(5, ('architect/engineer',)),
           Entry(6, ('locksmith/clockmaker',)),
           Entry(7, ('physician/apothecary',)),
           Entry(8, ('navigator/guide',)),
           Entry(9, ('alchemist/astrologer',)),
           Entry(10, ('spy/diplomat',)),
           Entry(11, ('cartographer',)),
           Entry(12, ('inventor',))))

Generator('official', d12,
          (Entry(1, ('town crier',)),
           Entry(2, ('tax collector',)),
           Entry(3, ('armiger/gentry',)),
           Entry(5, ('reeve/sheriff/constable',)),
           Entry(6, ('mayor/magistrate',)),
           Entry(7, ('priest/bishop/abbot',)),
           Entry(8, ('guildmaster',)),
           Entry(9, ('knight/templar',)),
           Entry(10, ('elder/high priest',)),
           Entry(11, ('noble (baron, etc.)',)),
           Entry(12, ('lord/lady/king/queen',))))

Generator('npc trait', d12,
          (Entry(1, ('npc trait physical appearance',)),
           Entry(7, ('npc trait personality',)),
           Entry(10, ('npc trait quirk',))))

Generator('npc trait physical appearance', d12,
          (Entry(1, ('disfigured (missing teeth, eye, etc.)',)),
           Entry(2, ('lasting injury (bad leg, arm, etc.)',)),
           Entry(3, ('tattooed/pockmarked/scarred',)),
           Entry(4, ('unkempt/shabby/grubby',)),
           Entry(5, ('big/thick/brawny',)),
           Entry(6, ('small/scrawny/emaciated',)),
           Entry(7, ('notable hair (wild, long, none, etc.)',)),
           Entry(8, ('notable nose (big, hooked, etc.)',)),
           Entry(9, ('notable eyes (blue, bloodshot, etc.)',)),
           Entry(10, ('clean/well-dressed/well-groomed',)),
           Entry(11, ('attractive/handsome/stunning',)),
           Entry(12, ('they are [roll again] despite [a contradictory detail of your choice]','npc trait physical appearance', 'npc trait physical appearance'))))

Generator('npc trait personality', d12,
          (Entry(1, ('loner/alienated/antisocial',)),
           Entry(2, ('cruel/belligerent/bully',)),
           Entry(3, ('anxious/fearful/cowardly',)),
           Entry(4, ('envious/covetous/greedy',)),
           Entry(5, ('aloof/haughty/arrogant',)),
           Entry(6, ('awkward/shy/self-loathing',)),
           Entry(7, ('orderly/compulsive/controlling',)),
           Entry(8, ('confident/impulsive/reckless',)),
           Entry(9, ('kind/generous/compassionate',)),
           Entry(10, ('easygoing/relaxed/peaceful',)),
           Entry(11, ('cheerful/happy/optimistic',)),
           Entry(12, ('they are [roll again] despite [a contradictory detail of your choice]','npc trait personality', 'npc trait personality'))))

Generator('npc trait quirk', d12,
          (Entry(1, ('insecure/racist/xenophobic',)),
           Entry(2, ('addict (sweets, drugs, sex, etc.)',)),
           Entry(3, ('phobia (spiders, fire, darkness, etc.)',)),
           Entry(4, ('allergic/asthmatic/chronically ill',)),
           Entry(5, ('skeptic/paranoid',)),
           Entry(6, ('superstitious/devout/fanatical',)),
           Entry(7, ('miser/pack-rat',)),
           Entry(8, ('spendthrift/wastrel',)),
           Entry(9, ('smart aleck/know-it-all',)),
           Entry(10, ('artistic/dreamer/delusional',)),
           Entry(11, ('naive/idealistic',)),
           Entry(12, ('they are [roll again] despite [a contradictory detail of your choice]','npc trait quirk', 'npc trait quirk'))))

# DETAILS ------------------------------------------------------------------------------------------

Generator('ability', d12,
          (Entry(1, ('bless/curse',)),
           Entry(2, ('entangle/trap/snare',)),
           Entry(3, ('poison/disease',)),
           Entry(4, ('paralyze/petrify',)),
           Entry(5, ('mimic/camouflage',)),
           Entry(6, ('seduce/hypnotize',)),
           Entry(7, ('dissolve/disintegrate',)),
           Entry(8, ('magic type',)),
           Entry(9, ('drain life/magic',)),
           Entry(10, ('immunity:', 'element')),
           Entry(11, ('read/control minds',)),
           Entry(12, ('ability','ability'))))

Generator('activity', d12,
          (Entry(1, ('laying trap/ambush',)),
           Entry(2, ('fighting/at war',)),
           Entry(3, ('prowling/on patrol',)),
           Entry(4, ('hunting/foraging',)),
           Entry(5, ('eating/resting',)),
           Entry(6, ('crafting/praying',)),
           Entry(7, ('traveling/relocating',)),
           Entry(8, ('exploring/lost',)),
           Entry(9, ('returning home',)),
           Entry(10, ('building/excavating',)),
           Entry(11, ('sleeping',)),
           Entry(12, ('dying',))))

Generator('adjective', d12,
          (Entry(1, ('slick/slimy',)),
           Entry(2, ('rough/hard/sharp',)),
           Entry(3, ('smooth/soft/dull',)),
           Entry(4, ('corroded/rusty',)),
           Entry(5, ('rotten/decaying',)),
           Entry(6, ('broken/brittle',)),
           Entry(7, ('stinking/smelly',)),
           Entry(8, ('weak/thin/drained',)),
           Entry(9, ('strong/fat/full',)),
           Entry(10, ('pale/poor/shallow',)),
           Entry(11, ('dark/rich/deep',)),
           Entry(12, ('colorful',))))

Generator('age', d12,
          (Entry(1, ('being born/built',)),
           Entry(2, ('young/recent',)),
           Entry(5, ('middle-aged',)),
           Entry(8, ('old',)),
           Entry(10, ('ancient',)),
           Entry(12, ('pre-historic',))))

Generator('alignement', d12,
          (Entry(1, ('Chaotic',)),
           Entry(3, ('Evil',)),
           Entry(5, ('Neutral',)),
           Entry(9, ('Good',)),
           Entry(11, ('Lawful',))))

Generator('aspect', d12,
          (Entry(1, ('power/strength',)),
           Entry(2, ('trickery/dexterity',)),
           Entry(3, ('time/constitution',)),
           Entry(4, ('knowledge/intelligence',)),
           Entry(5, ('nature/wisdom',)),
           Entry(6, ('culture/charisma',)),
           Entry(7, ('war/lies/discord',)),
           Entry(8, ('peace/truth/balance',)),
           Entry(9, ('hate/envy',)),
           Entry(10, ('love/admiration',)),
           Entry(11, ('element',)),
           Entry(12, ('aspect','aspect'))))

Generator('condition', d12,
          (Entry(1, ('being built/born',)),
           Entry(2, ('intact/healthy/stable',)),
           Entry(5, ('occupied/active/alert',)),
           Entry(8, ('worn/tired/weak',)),
           Entry(10, ('vacant/lost',)),
           Entry(11, ('ruined/defiled/dying',)),
           Entry(12, ('disappeared/dead',))))

Generator('disposition', d12,
          (Entry(1, ('attacking',)),
           Entry(2, ('hostile/aggressive',)),
           Entry(5, ('cautious/doubtful',)),
           Entry(7, ('fearful/fleeing',)),
           Entry(8, ('neutral',)),
           Entry(11, ('curious/hopeful',)),
           Entry(12, ('friendly',))))

Generator('element', d12,
          (Entry(1, ('air',)),
           Entry(3, ('earth',)),
           Entry(5, ('fire',)),
           Entry(7, ('water',)),
           Entry(9, ('life',)),
           Entry(11, ('death',))))

Generator('feature', d12,
          (Entry(1, ('heavily armored',)),
           Entry(2, ('winged/flying',)),
           Entry(4, ('multiple heads/headless',)),
           Entry(5, ('many eyes/one eye',)),
           Entry(6, ('many limbs/tails',)),
           Entry(7, ('tentacles/tendrils',)),
           Entry(8, ('aspect',)),
           Entry(9, ('element',)),
           Entry(10, ('magic type',)),
           Entry(11, ('oddity',)),
           Entry(12, ('feature','feature'))))

Generator('magic type', d12,
          (Entry(1, ('divination',)),
           Entry(3, ('enchantment',)),
           Entry(5, ('evocation',)),
           Entry(7, ('illusion',)),
           Entry(9, ('necromancy',)),
           Entry(11, ('summoning',))))

Generator('group number', d12,
          (Entry(1, ('Solitary (1)',)),
           Entry(5, ('group number (1d6 + 2)',)),
           Entry(10, ('Horde (4d6 per wave)',))))

Generator('oddity', d12,
          (Entry(1, ('weird color/smell/sound',)),
           Entry(2, ('geometric',)),
           Entry(3, ('web/network/system',)),
           Entry(4, ('crystalline/glass-like',)),
           Entry(5, ('fungal',)),
           Entry(6, ('gaseous/smokey',)),
           Entry(7, ('mirage/illusion',)),
           Entry(8, ('volcanic/explosive',)),
           Entry(9, ('magnetic/repellant',)),
           Entry(10, ('devoid of life',)),
           Entry(11, ('unexpectedly alive',)),
           Entry(12, ('oddity','oddity'))))

Generator('orientation', d12,
          (Entry(1, ('down/earthward',)),
           Entry(3, ('north',)),
           Entry(4, ('northeast',)),
           Entry(5, ('east',)),
           Entry(6, ('southeast',)),
           Entry(7, ('south',)),
           Entry(8, ('southwest',)),
           Entry(9, ('west',)),
           Entry(10, ('northwest',)),
           Entry(11, ('up/skyward',))))

Generator('ruination', d12,
          (Entry(1, ('arcane disaster',)),
           Entry(2, ('damnation/curse',)),
           Entry(3, ('earthquake/fire/flood',)),
           Entry(5, ('plague/famine/drought',)),
           Entry(7, ('overrun by monsters',)),
           Entry(9, ('war/invasion',)),
           Entry(11, ('depleted resources',)),
           Entry(12, ('better prospects elsewhere',))))

Generator('size', d12,
          (Entry(1, ('Tiny',)),
           Entry(2, ('Small',)),
           Entry(4, ('medium-sized',)),
           Entry(10, ('Large',)),
           Entry(12, ('Huge',))))

Generator('monster tag', d12,
          (Entry(1, ('Amorphous',)),
           Entry(2, ('Cautious',)),
           Entry(3, ('Construct',)),
           Entry(4, ('Devious',)),
           Entry(5, ('Intelligent',)),
           Entry(6, ('Magical',)),
           Entry(7, ('Organized',)),
           Entry(9, ('Planar',)),
           Entry(10, ('Stealthy',)),
           Entry(11, ('Terrifying',)),
           Entry(12, ('monster tag','monster tag'))))

Generator('terrain', d12,
          (Entry(1, ('wasteland/desert',)),
           Entry(2, ('flatland/plain',)),
           Entry(4, ('wetland/marsh/swamp',)),
           Entry(5, ('woodland/forest/jungle',)),
           Entry(8, ('highland/hills',)),
           Entry(10, ('mountains',)),
           Entry(12, ('oddity',))))

Generator('visibility', d12,
          (Entry(1, ('buried/camouflaged/nigh invisible',)),
           Entry(3, ('partly covered/over-grown/hidden',)),
           Entry(7, ('obvious/in plain sight',)),
           Entry(10, ('visible at near distance',)),
           Entry(12, ('visible at great distance/focal point',))))

# CUSTOM -------------------------------------------------------------------------------------------


Generator('binding', d12,
          (Entry(1, ('mask',)),
           Entry(2, ('bones',)),
           Entry(3, ('chains/rope/ribbon',)),
           Entry(4, ('words/names/runes',)),
           Entry(5, ('ring',)),
           Entry(6, ('halo/light/shadow',)),
           Entry(7, ('scar/tatoo',)),
           Entry(8, ('gem/jewelry',)),
           Entry(9, ('shared blood/flesh',)),
           Entry(10, ('key',)),
           Entry(11, ('silver/gold/mithril',)),
           Entry(12, ('weapon',))))

def main():
    try:
        previous_generator_name = 'discovery'
        while True:
            generator_name = input('Enter a generator name (default: '
                                   + previous_generator_name
                                   + '): ')
            if generator_name == 'ls':
                print(', '.join(generators.keys()))
            elif generator_name == '':
                generators[previous_generator_name].generate_print()
            elif generator_name in generators:
                generators[generator_name].generate_print()
                previous_generator_name = generator_name
            else:
                print(generator_name + ': not found')
    except KeyboardInterrupt:
        print('Quitting')

if __name__ == '__main__':
    main()
