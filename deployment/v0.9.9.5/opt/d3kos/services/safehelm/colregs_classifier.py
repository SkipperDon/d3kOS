# colregs_classifier.py
"""COLREGs Rules 13/14/15/18 classification. Pure; no gating, no I/O.

Relative bearing convention: degrees clockwise from own COG.
0 = dead ahead, 90 = starboard beam, 180 = astern, 270 = port beam.
22.5 deg abaft the beam = 112.5 (starboard) and 247.5 (port) — the Rule 13(b) boundary.
"""

ABAFT_STBD = 112.5
ABAFT_PORT = 247.5
HEADON_COURSE_MIN  = 165.0   # reciprocal within 15 deg
HEADON_BEARING_TOL = 22.5    # target must be roughly ahead
OVERTAKE_COURSE_MAX = 67.5   # overtaking implies broadly similar courses

# Dead-band on the overtaking speed comparison. A strict `>` on two noisy AIS
# SOG reports makes near-equal-speed vessels flap between rule13_being_overtaken
# and no_situation tick to tick, which under ADV-4 would alternate voice phrases
# for what is one unchanging situation. Same anti-flap intent as
# SafeHelmAlertManager.CLEAR_HYSTERESIS, applied to speed instead of CPA.
OVERTAKE_SOG_DEADBAND_KTS = 0.5

# Rule 13(d) lock. Once an overtaking situation exists it persists until the
# vessels are finally past and clear; a bearing change cannot convert it into a
# crossing. Both roles lock: the overtaking vessel stays give-way, and the
# overtaken vessel stays stand-on.
RULE13_LOCKED = frozenset({'rule13_being_overtaken',
                           'rule13_being_overtaken_unconfirmed',
                           'rule13_overtaking'})

# "Finally past and clear" has no numeric definition in the regulations.
# Tunable #5 -- see §12.3 item 6a.
PAST_AND_CLEAR_RANGE_M = 500.0


def _course_diff(a, b):
    """Angle between two headings, 0..180. 0 = same direction, 180 = reciprocal."""
    return abs((b - a + 180.0) % 360.0 - 180.0)


def _relative_bearing_of_me_from_target(own_cog, tgt_cog, rb):
    true_brg_tgt_from_me = (own_cog + rb) % 360.0
    true_brg_me_from_tgt = (true_brg_tgt_from_me + 180.0) % 360.0
    return (true_brg_me_from_tgt - tgt_cog) % 360.0


# Rule 18(a): a power-driven vessel keeps clear of these regardless of geometry.
# Normalised from design.aisShipType and navigation.state -- map the raw AIS
# enumerations against ITU-R M.1371 at implementation time (§11).
RULE18_OUTRANKS_US = frozenset({
    'not-under-command',
    'restricted-manoeuverability',
    'engaged-in-fishing',
    'sailing',
})


def classify(own_cog, own_sog, tgt_cog, tgt_sog, relative_bearing,
             tgt_class=None, prior_rule=None, is_past_and_clear=False,
             in_sight=False):
    """Returns one of:
         'rule13_being_overtaken'      we are STAND-ON; Rule 13 overrides Rule 18
         'rule13_overtaking'           we are GIVE-WAY; keep clear
         'rule18_giveway'              target outranks us; we give way whatever the geometry
         'rule14_headon'               both alter to starboard
         'rule15_giveway'              target on our starboard; we give way
         'rule15_standon'              target on our port; we stand on
         'rule15_standon_unconfirmed'  geometry says stand-on, target type unknown
         'no_situation'

    tgt_class: normalised target category, or None when AIS has not supplied
        it. None is common -- Class B position reports carry no navigational
        status and static data is infrequent -- so it must never be treated as
        "power-driven".
    """
    rb = relative_bearing % 360.0
    cdiff = _course_diff(own_cog, tgt_cog)

    # --- Rule 13(d): an established overtaking situation PERSISTS. ---
    # "Any subsequent alteration of the bearing between the two vessels shall
    #  not make the overtaking vessel a crossing vessel within the meaning of
    #  these Rules or relieve her of the duty of keeping clear of the
    #  overtaken vessel until she is finally past and clear."
    # Evaluated before the geometry, because the geometry is exactly what
    # 13(d) forbids us from re-reading mid-encounter.
    if prior_rule in RULE13_LOCKED and not is_past_and_clear:
        return prior_rule

    # --- Rule 13 next: it overrides 14, 15 and 18 (13(a) "notwithstanding") ---
    if cdiff < OVERTAKE_COURSE_MAX:
        if (ABAFT_STBD < rb < ABAFT_PORT
                and tgt_sog - own_sog > OVERTAKE_SOG_DEADBAND_KTS):
            # Rule 13 is in Section II, so Rule 11 gates it too: this asserts
            # STAND-ON and must not do so for a target not confirmed in sight.
            # Unconfirmed still yields useful, regulation-grounded advice --
            # Rule 19(d)(ii) says avoid altering TOWARDS a vessel abaft the
            # beam, which holds whether or not Section II applies.
            if not in_sight:
                return 'rule13_being_overtaken_unconfirmed'
            return 'rule13_being_overtaken'          # they overtake us -> we stand on
        rb_me = _relative_bearing_of_me_from_target(own_cog, tgt_cog, rb)
        if (ABAFT_STBD < rb_me < ABAFT_PORT
                and own_sog - tgt_sog > OVERTAKE_SOG_DEADBAND_KTS):
            return 'rule13_overtaking'               # we overtake them -> we give way
        # --- Rule 13(c): "When a vessel is in any doubt as to whether she is
        #     overtaking another, she shall assume that this is the case and
        #     act accordingly." We are abaft the target's beam but the speed
        #     differential is inside the AIS noise floor, so whether we are
        #     gaining is genuinely unknown. Assume we are -> take the GIVE-WAY
        #     role. Note the asymmetry: 13(c) biases toward the give-way role
        #     only. It must never be used to manufacture a stand-on claim,
        #     which is the verdict that tells the captain to hold course.
        if (ABAFT_STBD < rb_me < ABAFT_PORT
                and 0.0 < own_sog - tgt_sog <= OVERTAKE_SOG_DEADBAND_KTS):
            return 'rule13_overtaking'

    # --- Rule 18(a): target outranks us. Sits after Rule 13 (whose preamble
    #     excepts it) and before Rules 14/15, which it overrides entirely. ---
    if tgt_class in RULE18_OUTRANKS_US:
        return 'rule18_giveway'

    # --- Rule 14: reciprocal courses AND target roughly ahead ---
    if cdiff > HEADON_COURSE_MIN and (rb <= HEADON_BEARING_TOL
                                      or rb >= 360.0 - HEADON_BEARING_TOL):
        return 'rule14_headon'

    # --- Rule 15: crossing ---
    if rb <= ABAFT_STBD:
        return 'rule15_giveway'                      # target to starboard
    if rb >= ABAFT_PORT:
        # Stand-On is the dangerous verdict: it tells the captain to hold
        # course. Two independent reasons forbid asserting it on unconfirmed
        # data (§14.3 option B):
        #   Rule 18 -- an unidentified target may be a sailing or fishing
        #     vessel that outranks us.
        #   Rule 11 -- Rules 11-18 apply only to vessels IN SIGHT of one
        #     another, and AIS never establishes that. In restricted
        #     visibility Rule 19 applies and there is no stand-on vessel,
        #     so "hold course and speed" would be actively wrong.
        if tgt_class is None or not in_sight:
            return 'rule15_standon_unconfirmed'
        return 'rule15_standon'                      # target to port
    return 'no_situation'


HEADON_RULES = frozenset({'rule14_headon'})          # drives the +2 min TCPA bonus

VOICE_PHRASES = {
    # D02-6 — advisory form. Was: 'Danger. Head-on situation. Alter course to starboard.'
    'rule14_headon':          'Danger. Head-on situation. '
                              'COLREGs require starboard alteration.',
    'rule15_giveway':         'Warning. Crossing target to starboard. You are Give-Way.',
    'rule15_standon':         'Alert. Crossing target to port. You are Stand-On. Monitor.',

    # NEW in v1.1 — replaces v1.0's inverted single 'rule13_overtake' phrase.
    # D02-6 advisory form applied to both, operator-approved S160.
    'rule13_being_overtaken': 'Alert. Vessel overtaking from astern. You are Stand-On. '
                              'COLREGs require you to hold course and speed.',
    'rule13_overtaking':      'Warning. You are overtaking. You are Give-Way. '
                              'COLREGs require you to keep clear.',

    # NEW v1.4 — Rule 18(a). Target outranks a power-driven vessel.
    'rule18_giveway':         'Warning. {target_kind} ahead. You are Give-Way. '
                              'COLREGs require you to keep clear.',

    # NEW v1.7 — Rule 13 is in Section II, so Rule 11 gates it. Gives the
    # Rule 19(d)(ii) guidance, which is valid under either rule set.
    'rule13_being_overtaken_unconfirmed':
                              'Alert. Vessel overtaking from astern. Not confirmed in '
                              'sight, so Stand-On may not apply. COLREGs advise against '
                              'altering course towards it.',

    # NEW v1.4 — geometry says Stand-On but the target type is unknown, which is
    # the common case for Class B AIS. Does not assert a role it cannot support.
    'rule15_standon_unconfirmed':
                              'Alert. Crossing target to port. Vessel type unconfirmed. '
                              'COLREGs may require you to give way. Monitor.',

    'critical':               'Critical collision risk. Target {bearing}. CPA {cpa_m} metres.',
}
