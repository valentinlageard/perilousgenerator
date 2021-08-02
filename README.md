# Perilous generator

*DungeonWorld* generators based on the *Perilous Wilds*.

## Usage

`git clone https://github.com/valentinlageard/perilousgenerator.git`

`cd perilousgenerator`

`python3 perilousgenerator.py`

Once the program launched :
- Enter a valid generator name to call it. Once a valid generator was entered, pressing Enter recalls the generator.
- `ls` to list all generators.

General generators :
- discovery
- danger
- dungeon exploration

## Example outputs

```
 └─discovery
    ├─evidence
    │  └─tracks/spoor
    │     ├─definite/clear
    │     ├─age
    │     │  └─middle-aged
    │     ├─creature responsible
    │     └─creature
    │        └─beast
    │           ├─beast earthbound
    │           │  └─termite/tick/louse
    │           ├─activity
    │           │  └─hunting/foraging
    │           ├─disposition
    │           │  └─hostile/aggressive
    │           ├─group number
    │           │  └─Solitary (1)
    │           └─size
    │              └─Small
    └─Consider the implications and be ready for them to take the bait.
```

```
 └─danger
    ├─hazard (threaten them and their stuff)
    └─hazard
       └─hazard unnatural
          ├─taint/blight/curse
          ├─aspect
          │  └─hate/envy
          └─visibility
             └─obvious/in plain sight
```

```
 └─dungeon exploration
    ├─themed area, unique
    ├─dungeon discovery
    │  └─dungeon discovery feature
    │     └─pillars/columns
    └─dungeon danger
       └─dungeon danger trap
          ├─dungeon danger trap
          │  └─alarm
          └─dungeon danger trap
             └─alarm
```
