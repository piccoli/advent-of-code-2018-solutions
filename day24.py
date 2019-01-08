#! /usr/bin/env python3
import sys, re, math

from copy import deepcopy
from functools import partial

verbose = len(sys.argv) > 1 and sys.argv[1] == '--verbose'
log = partial(print, flush = True, file = sys.stderr) if verbose\
    else (lambda *a, **k: None)

AttackTypes = Slashing, Radiation, Fire, Cold, Bludgeoning =\
        'slashing', 'radiation', 'fire', 'cold', 'bludgeoning'

ImmuneSystem, Infection = 'Immune System', 'Infection'

class Group:
    def __init__(self, army, index, size, hit_points, immunities, weaknesses, attack_type, attack_damage, initiative):
        self.army          = army
        self.index         = index
        self.size          = size
        self.hit_points    = hit_points
        self.immunities    = immunities
        self.weaknesses    = weaknesses
        self.attack_type   = attack_type
        self.attack_damage = attack_damage
        self.initiative    = initiative

def parse_input():
    m = None
    def match(pattern, string):
        nonlocal m
        m = re.match(pattern, string)
        return m

    current_army = None
    army = {
        ImmuneSystem: [],
        Infection: []
    }

    attack_type_pattern = '({})'.format('|'.join(AttackTypes))
    damage_list_pattern = '{}(, {})?(, {})?'.format(
        attack_type_pattern,
        attack_type_pattern,
        attack_type_pattern
    )

    for line in sys.stdin.readlines():
        line = line.strip()

        if not line:
            continue

        if match(r'((Immune System)|(Infection)):$', line):
            current_army = m.group(1)
        # TODO Re-write here. Unfortunately, Python's `re` module does
        # not support repeated capturing groups, thus it might be cleaner to
        # to tokenize and perform syntax-directed parsing here.
        elif match((
            r'(\d+) units each with (\d+) hit points( \('\
          + r'((immune|weak) to {})(; (immune|weak) to {})?\))? '\
          + r'with an attack that does (\d+) {} damage at initiative (\d+)').format(
                damage_list_pattern,
                damage_list_pattern,
                attack_type_pattern
            ), line):

            d1 = [ None ] * 3
            d2 = [ None ] * 3
            size, hit_points, defense_type1, d1[0], d1[1], d1[2],\
            defense_type2, d2[0], d2[1], d2[2], damage, attack_type, initiative =\
                map(m.group, (1, 2, 5, 6, 8, 10, 12, 13, 15, 17, 18, 19, 20))

            size, hit_points, damage, initiative = map(
                int, (size, hit_points, damage, initiative)
            )

            defenses = { 'weak': (), 'immune': () }
            defenses[defense_type1] = tuple(d for d in d1 if d)
            defenses[defense_type2] = tuple(d for d in d2 if d)

            army[current_army].append(Group(
                army          = current_army,
                index         = len(army[current_army]) + 1,
                size          = size,
                hit_points    = hit_points,
                immunities    = defenses['immune'],
                weaknesses    = defenses['weak'],
                attack_type   = attack_type,
                attack_damage = damage,
                initiative    = initiative
            ))

    return army

def select_targets(army):
    all_groups = sorted(
        army[ImmuneSystem] + army[Infection],
        reverse = True,
        key = lambda g: (g.size * g.attack_damage, g.initiative)
    )

    targeted     = set()
    target       = {}
    damage_dealt = {}
    for group in all_groups:
        opposing_army = army[Infection] if group.army == ImmuneSystem\
                   else army[ImmuneSystem]

        enemies = [ e for e in opposing_army if e not in targeted ]

        damage_dealt.update({
            (group, e): (
                     0                       if group.attack_type in e.immunities
                else group.attack_damage * 2 if group.attack_type in e.weaknesses
                else group.attack_damage
            )
            for e in enemies
        })

        if not enemies:
            target[group] = None
            continue

        for e in enemies:
            if damage_dealt[group, e] > 0:
                log('{} group {} would deal defending group {} {} damage'.format(
                    group.army,
                    group.index,
                    e.index,
                    group.size * damage_dealt[group, e]
                ))

        selected = max(enemies, key = lambda e: (
            damage_dealt[group, e],
            e.size * e.attack_damage,
            e.initiative
        ))

        if damage_dealt[group, selected] > 0:
            targeted.add(selected)
            target[group] = selected
        else:
            target[group] = None

    return target, damage_dealt

def attack(army, target, damage_dealt):
    all_groups = sorted(
        army[ImmuneSystem] + army[Infection],
        reverse = True,
        key = lambda g: g.initiative
    )

    log()
    for group in all_groups:
        if group.size == 0:
            continue

        selected = target[group]

        if not selected:
            continue

        damage = group.size * damage_dealt[group, selected]

        remaining_hits = max(0, selected.size * selected.hit_points - damage)

        remaining = 0 if selected.size == 0\
                else int(math.ceil(remaining_hits / selected.hit_points))

        log('{} group {} attacks defending group {}, killing {} units'.format(
            group.army,
            group.index,
            selected.index,
            selected.size - remaining
        ))

        selected.size = remaining

def fight(army):
    while len(army[ImmuneSystem]) > 0 and len(army[Infection]) > 0:
        print_armies(army)
        log()

        target, damage_dealt = select_targets(army)

        # Stalemate (one army is immune to all attack types in the opposing army)
        if all(t is None for t in target.values()):
            log('Stalemate! Cannot continue battle.')
            return

        attack(army, target, damage_dealt)

        army[ImmuneSystem] = [ g for g in army[ImmuneSystem] if g.size > 0 ]
        army[Infection]    = [ g for g in army[Infection]    if g.size > 0 ]

def print_armies(army):
    for army, groups in army.items():
        log('{}:'.format(army))

        if len(groups) == 0:
            log('No groups remain.')

        for group in groups:
            log('Group {} contains {} units'.format(group.index, group.size))
            #log('\tArmy:'         , group.army)
            #log('\tHit Points:'   , group.hit_points)
            #log('\tImmunities:'   , ', '.join(group.immunities))
            #log('\tWeaknesses:'   , ', '.join(group.weaknesses))
            #log('\tAttack Type:'  , group.attack_type)
            #log('\tAttack Damage:', group.attack_damage)
            #log('\tInitiative:'   , group.initiative)

def find_boost(army, max_boost = 0):
    l = 0
    u = max_boost

    remaining = {
        ImmuneSystem: 0,
        Infection: 0
    }

    while l <= u:
        copy = deepcopy(army)
        boost = (l + u) // 2

        for g in copy[ImmuneSystem]:
            g.attack_damage += boost

        fight(copy)

        remaining[ImmuneSystem] = sum(g.size for g in copy[ImmuneSystem])
        remaining[Infection]    = sum(g.size for g in copy[Infection])

        if remaining[Infection] == 0 and remaining[ImmuneSystem] > 0:
            u = boost - 1
        else:
            l = boost + 1

    return max(remaining.values())

army = parse_input()
print(find_boost(army))

max_boost = sum(g.size * g.hit_points for g in army[Infection])
print(find_boost(army, max_boost))
