"""C1-C8 -- COLREGs classifier guard tests (V09995-SOL-001 §8.4, §10.1, §12).

These are the guards for the two safety-critical defects in solution design v1.0:

  * Rule 14 head-on was tested with `course_diff < 15`. With the formula used,
    0 means parallel/same-direction and 180 means reciprocal -- so it fired for
    vessels travelling TOGETHER and never for an actual head-on.   -> C3, C4
  * Rule 13 role was inverted. Relative bearing 112.5-247.5 is abaft own beam;
    a target there is overtaking US, so under Rule 13(a) WE are stand-on. v1.0
    voiced "You do not have right-of-way."                          -> C1, C2

Relative bearing convention: degrees clockwise from own COG.
0 = dead ahead, 90 = starboard beam, 180 = astern, 270 = port beam.
"""
import pytest

from conftest import lazy_module

SPEC = '§8.4'


@pytest.fixture
def cc():
    return lazy_module('colregs_classifier', SPEC)


# --------------------------------------------------------------------------
# Rule 13 -- overtaking. Overrides Rules 14 and 15 ("notwithstanding", 13(a)).
# --------------------------------------------------------------------------

def test_c1_target_astern_and_faster_means_we_are_stand_on(cc):
    """C1: target abaft our beam, closing faster -> THEY overtake US.

    Rule 13(a) puts the duty to keep clear on the overtaking vessel, so we are
    STAND-ON and must hold course and speed.

    v1.0 returned an overtaking classification whose voice line said
    "You do not have right-of-way" -- telling the captain to give way while
    obliged to hold course. This is the defect this test exists for.
    """
    assert cc.classify(own_cog=90, own_sog=10,
                       tgt_cog=90, tgt_sog=12,
                       relative_bearing=180) == 'rule13_being_overtaken'


def test_c2_we_are_faster_and_target_ahead_means_we_give_way(cc):
    """C2: we are coming up on a slower vessel from abaft ITS beam -> we GIVE WAY.

    v1.0 classified this as `rule15_giveway`. The role happened to be right but
    the rule was wrong: Rule 13 overrides Rule 15 in an overtaking situation,
    and the advice a captain needs differs.
    """
    assert cc.classify(own_cog=90, own_sog=12,
                       tgt_cog=90, tgt_sog=8,
                       relative_bearing=0) == 'rule13_overtaking'


def test_c7_no_rule_13_without_a_speed_differential(cc):
    """C7: target just abaft the beam at equal speed is not an overtaking case.

    Neither vessel is "coming up with" the other, so Rule 13 does not apply,
    and bearing 113 deg is outside both Rule 15 sectors.
    """
    assert cc.classify(own_cog=90, own_sog=10,
                       tgt_cog=90, tgt_sog=10,
                       relative_bearing=113.0) == 'no_situation'


# --------------------------------------------------------------------------
# Rule 14 -- head-on. Reciprocal courses AND target roughly ahead.
# --------------------------------------------------------------------------

def test_c3_reciprocal_courses_dead_ahead_is_head_on(cc):
    """C3: own 090, target 270, dead ahead -> Rule 14.

    v1.0 FAILED this. Its test was `course_diff < 15`; here course_diff is 180,
    so it fell through to the crossing branch and a genuine head-on was never
    classified as one.
    """
    assert cc.classify(own_cog=90, own_sog=10,
                       tgt_cog=270, tgt_sog=10,
                       relative_bearing=0) == 'rule14_headon'


def test_c4_near_identical_courses_are_not_head_on(cc):
    """C4: own 090, target 095, equal speed -> must NOT be Rule 14.

    v1.0 returned `rule14_headon` here and would have announced
    "Danger. Head-on situation." to two boats cruising alongside each other.
    This is the inverted-comparison guard.
    """
    result = cc.classify(own_cog=90, own_sog=10,
                         tgt_cog=95, tgt_sog=10,
                         relative_bearing=45)
    assert result != 'rule14_headon'
    # Pure geometry puts the target on our starboard bow. Whether it matters at
    # all is decided by the §8.2 gate, not here.
    assert result == 'rule15_giveway'


# --------------------------------------------------------------------------
# Rule 15 -- crossing.
# --------------------------------------------------------------------------

def test_c5_target_on_starboard_means_we_give_way(cc):
    """C5: crossing target to starboard -> we keep out of the way (Rule 15)."""
    assert cc.classify(own_cog=0, own_sog=10,
                       tgt_cog=270, tgt_sog=10,
                       relative_bearing=45) == 'rule15_giveway'


def test_c6_target_on_port_means_we_stand_on(cc):
    """C6: crossing target to port -> we hold course and speed (Rule 15/17)."""
    assert cc.classify(own_cog=0, own_sog=10,
                       tgt_cog=90, tgt_sog=10,
                       relative_bearing=315) == 'rule15_standon'


# --------------------------------------------------------------------------
# Advisory-language guard (ADV-4 / D02-6).
# --------------------------------------------------------------------------

IMPERATIVE_OPENERS = ('alter', 'hold', 'keep', 'turn', 'reduce', 'steer', 'stop')


def test_c8_no_voice_phrase_issues_an_imperative_command(cc):
    """C8: every phrase states a fact, a role, or what COLREGs require.

    D02-6: an advisory system issuing a command shifts liability from the
    captain to the software. v1.0 said "Alter course to starboard."

    Guard: no sentence within a phrase may OPEN with an imperative verb.
    "COLREGs require starboard alteration" passes; "Alter course" does not.
    """
    phrases = getattr(cc, 'VOICE_PHRASES', None)
    assert phrases, 'VOICE_PHRASES missing from colregs_classifier (§8.4)'

    offenders = []
    for key, phrase in phrases.items():
        for sentence in phrase.split('.'):
            first = sentence.strip().split(' ')[0].lower().strip(',')
            if first in IMPERATIVE_OPENERS:
                offenders.append((key, sentence.strip()))
    assert not offenders, (
        'Imperative voice phrasing found -- violates D02-6/ADV-4. '
        'State what COLREGs require instead of commanding the captain: '
        f'{offenders}'
    )


def test_c8b_no_phrase_asserts_that_water_is_clear(cc):
    """C8b (ADV-4): silence means "no qualifying AIS target", never "clear water"."""
    phrases = getattr(cc, 'VOICE_PHRASES', None)
    assert phrases, 'VOICE_PHRASES missing from colregs_classifier (§8.4)'

    banned = ('all clear', 'water is clear', 'no risk', 'safe to', 'you are clear')
    offenders = [(k, p) for k, p in phrases.items()
                 if any(b in p.lower() for b in banned)]
    assert not offenders, f'Phrase asserts safety/clearance -- violates ADV-4: {offenders}'


def test_c8c_every_classification_has_a_voice_phrase(cc):
    """C8c: a rule the classifier can return but cannot voice is a silent gap."""
    phrases = getattr(cc, 'VOICE_PHRASES', {})
    required = {'rule13_being_overtaken', 'rule13_overtaking',
                'rule14_headon', 'rule15_giveway', 'rule15_standon'}
    missing = required - set(phrases)
    assert not missing, f'Classifications with no voice phrase: {sorted(missing)}'


# --------------------------------------------------------------------------
# C9-C10 -- overtaking SOG dead-band (§8.4). Added v1.3 after external review.
#
# The overtaking test was a strict `>` on two AIS-reported SOGs. Two vessels
# running near-identical speed with noisy reports would flap between
# rule13_being_overtaken and no_situation tick to tick, alternating voice
# phrases for one unchanging situation. Same anti-flap intent as
# SafeHelmAlertManager.CLEAR_HYSTERESIS, applied to speed instead of CPA.
# --------------------------------------------------------------------------

def test_c9_near_equal_speed_does_not_register_as_overtaking(cc):
    """C9: a 0.2 kt differential is inside the dead-band -> no Rule 13."""
    assert cc.OVERTAKE_SOG_DEADBAND_KTS == pytest.approx(0.5)
    assert cc.classify(own_cog=90, own_sog=10.0,
                       tgt_cog=90, tgt_sog=10.2,
                       relative_bearing=180) == 'no_situation'


def test_c9b_dead_band_is_symmetric(cc):
    """C9b: the same dead-band applies when we are the faster vessel."""
    assert cc.classify(own_cog=90, own_sog=10.2,
                       tgt_cog=90, tgt_sog=10.0,
                       relative_bearing=0) != 'rule13_overtaking'


def test_c10_clear_speed_differential_still_registers(cc):
    """C10: the dead-band must not suppress a real overtaking situation."""
    assert cc.classify(own_cog=90, own_sog=10.0,
                       tgt_cog=90, tgt_sog=11.0,
                       relative_bearing=180) == 'rule13_being_overtaken'


def test_c10b_no_flapping_across_a_noisy_sog_sequence(cc):
    """C10b: jittering SOG around parity must yield one stable answer.

    Simulates +/- 0.3 kt of AIS noise on a target running at our speed. Every
    tick must classify identically, or the captain hears alternating phrases.
    """
    results = {
        cc.classify(own_cog=90, own_sog=10.0, tgt_cog=90,
                    tgt_sog=10.0 + jitter, relative_bearing=180)
        for jitter in (-0.3, -0.15, 0.0, 0.15, 0.3)
    }
    assert len(results) == 1, f'classification flapped across SOG noise: {results}'
