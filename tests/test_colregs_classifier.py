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
    """C6: crossing target to port -> we hold course and speed (Rule 15/17).

    tgt_class must be stated. Since v1.4 an unconfirmed target cannot be told
    it is Stand-On, because it may be a sailing or fishing vessel that outranks
    us under Rule 18 -- see C13. The unconfirmed path is asserted separately.
    """
    assert cc.classify(own_cog=0, own_sog=10,
                       tgt_cog=90, tgt_sog=10,
                       relative_bearing=315,
                       tgt_class='power-driven') == 'rule15_standon'


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


def test_c9b_dead_band_yields_to_rule_13c_on_the_give_way_side(cc):
    """C9b: v1.3 asserted the dead-band was symmetric. Rule 13(c) supersedes that.

    A sub-dead-band differential in OUR favour is exactly the doubt 13(c)
    addresses: assume we are overtaking and take the give-way role. The
    dead-band was an engineering anti-flap choice; 13(c) is regulation text,
    and it resolves the same flapping deterministically rather than by
    suppressing the classification.

    The asymmetry is deliberate and is the point of C15b: 13(c) creates a duty,
    never a privilege, so it applies on the give-way side only.
    """
    assert cc.classify(own_cog=90, own_sog=10.2,
                       tgt_cog=90, tgt_sog=10.0,
                       relative_bearing=0) == 'rule13_overtaking'


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


# --------------------------------------------------------------------------
# C11-C13 -- Rule 18(a) responsibilities between vessels. Added v1.4.
#
# Rules 13/14/15 govern two POWER-DRIVEN vessels. v1.3 assumed that and never
# checked. Rule 18(a), verified against the IMO text S160:
#   "Except where Rules 9, 10 and 13 otherwise require: (a) A power-driven
#    vessel underway shall keep out of the way of: (i) a vessel not under
#    command; (ii) a vessel restricted in her ability to manoeuvre;
#    (iii) a vessel engaged in fishing; (iv) a sailing vessel."
#
# So v1.3 would have announced "You are Stand-On" to a captain obliged to keep
# clear -- the same failure as the original Rule 13 inversion.
# --------------------------------------------------------------------------

RULE18_CLASSES = ['sailing', 'engaged-in-fishing',
                  'not-under-command', 'restricted-manoeuverability']


@pytest.mark.parametrize('tgt_class', RULE18_CLASSES)
def test_c11_rule18_target_overrides_crossing_geometry(cc, tgt_class):
    """C11: geometry says we stand on; Rule 18 says we give way. Rule 18 wins.

    Target to port (rb 315) would be rule15_standon between two power-driven
    vessels. It is not, if the target outranks us.
    """
    assert cc.classify(own_cog=0, own_sog=10, tgt_cog=90, tgt_sog=6,
                       relative_bearing=315,
                       tgt_class=tgt_class) == 'rule18_giveway'


def test_c11b_rule18_does_not_override_rule_13(cc):
    """C11b: Rule 18's own preamble excepts Rule 13.

    If a sailing vessel is overtaking us, Rule 13(a) still makes the overtaking
    vessel keep clear, so we remain STAND-ON. Ordering matters: Rule 13 is
    evaluated before Rule 18.
    """
    assert cc.classify(own_cog=90, own_sog=10, tgt_cog=90, tgt_sog=12,
                       relative_bearing=180,
                       tgt_class='sailing') == 'rule13_being_overtaken'


def test_c12_confirmed_power_driven_target_still_gives_stand_on(cc):
    """C12: Rule 18 must not swallow the ordinary Rule 15 stand-on case."""
    assert cc.classify(own_cog=0, own_sog=10, tgt_cog=90, tgt_sog=10,
                       relative_bearing=315,
                       tgt_class='power-driven') == 'rule15_standon'


def test_c13_unknown_target_type_never_asserts_stand_on(cc):
    """C13: THE SAFETY GUARD. Stand-On is the dangerous verdict.

    Stand-On tells the captain to hold course. Give-Way is conservative. An
    unknown target may be a sailing or fishing vessel that outranks us under
    Rule 18 -- and unknown is the COMMON case, because Class B AIS position
    reports carry no navigational status and static data is infrequent.
    """
    result = cc.classify(own_cog=0, own_sog=10, tgt_cog=90, tgt_sog=10,
                         relative_bearing=315, tgt_class=None)
    assert result != 'rule15_standon', (
        'asserted Stand-On for a target whose type could not be confirmed')
    assert result == 'rule15_standon_unconfirmed'


def test_c13b_unconfirmed_phrase_does_not_assert_a_role(cc):
    """C13b: the unconfirmed phrase must hedge, not claim Stand-On."""
    phrase = cc.VOICE_PHRASES['rule15_standon_unconfirmed'].lower()
    assert 'unconfirmed' in phrase
    assert 'may require' in phrase, 'phrase must hedge the role, not assert it'
    assert 'you are stand-on' not in phrase


def test_c13c_tgt_class_defaults_to_unknown(cc):
    """C13c: omitting tgt_class must behave as unknown, never as power-driven.

    A caller that forgets the argument must fail safe.
    """
    assert cc.classify(own_cog=0, own_sog=10, tgt_cog=90, tgt_sog=10,
                       relative_bearing=315) == 'rule15_standon_unconfirmed'


# --------------------------------------------------------------------------
# C14-C16 -- Rule 13(c) and 13(d). Added v1.5 after a third external review.
#
# The review cited "Rule 13(c)" for the persistence requirement; the IMO text
# (verified S160) puts it at 13(d), and 13(c) is a separate in-doubt rule that
# was ALSO unimplemented. Both are now covered.
#
#   13(c) "When a vessel is in any doubt as to whether she is overtaking
#          another, she shall assume that this is the case and act accordingly."
#   13(d) "Any subsequent alteration of the bearing between the two vessels
#          shall not make the overtaking vessel a crossing vessel within the
#          meaning of these Rules or relieve her of the duty of keeping clear
#          of the overtaken vessel until she is finally past and clear."
# --------------------------------------------------------------------------

def test_c14_overtaking_does_not_become_crossing_when_the_bearing_moves(cc):
    """C14: THE RULE 13(d) GUARD. A ferry overtaking us stays an overtaking case.

    A fast ferry comes up from our quarter (rb 120, abaft our beam) and we are
    correctly STAND-ON. As it draws level and forward, its bearing slides to
    rb 95 -- forward of the 112.5 deg boundary. Instantaneous geometry would
    now read "target on our starboard bow" and hand us Rule 15 GIVE-WAY.

    Rule 13(d) forbids exactly that. We remain stand-on until it is finally
    past and clear. v1.4 evaluated geometry per tick with no memory and would
    have flipped the captain's role mid-encounter -- the same class of error as
    the v1.0 inversions, occurring at the worst possible moment.
    """
    established = cc.classify(own_cog=0, own_sog=10, tgt_cog=5, tgt_sog=18,
                              relative_bearing=120, tgt_class='power-driven')
    assert established == 'rule13_being_overtaken'

    still = cc.classify(own_cog=0, own_sog=10, tgt_cog=5, tgt_sog=18,
                        relative_bearing=95, tgt_class='power-driven',
                        prior_rule=established, is_past_and_clear=False)
    assert still == 'rule13_being_overtaken', (
        'Rule 13(d) violated: a bearing change converted an overtaking '
        'situation into a crossing and flipped the captain to give-way')


def test_c14b_the_lock_also_holds_the_give_way_role(cc):
    """C14b: 13(d) binds the overtaking vessel too -- it cannot shed give-way."""
    still = cc.classify(own_cog=0, own_sog=18, tgt_cog=5, tgt_sog=10,
                        relative_bearing=45, tgt_class='power-driven',
                        prior_rule='rule13_overtaking', is_past_and_clear=False)
    assert still == 'rule13_overtaking'


def test_c14c_lock_releases_once_finally_past_and_clear(cc):
    """C14c: 13(d) ends at "finally past and clear", not before and not never.

    A lock that never released would pin a stale role for the rest of the
    passage.
    """
    result = cc.classify(own_cog=0, own_sog=10, tgt_cog=180, tgt_sog=10,
                         relative_bearing=0, tgt_class='power-driven',
                         prior_rule='rule13_being_overtaken',
                         is_past_and_clear=True)
    assert result == 'rule14_headon', 'lock did not release when past and clear'


def test_c14d_lock_does_not_apply_to_non_rule_13_priors(cc):
    """C14d: only Rule 13 persists. A crossing situation is re-evaluated freely."""
    result = cc.classify(own_cog=0, own_sog=10, tgt_cog=180, tgt_sog=10,
                         relative_bearing=0, tgt_class='power-driven',
                         prior_rule='rule15_giveway', is_past_and_clear=False)
    assert result == 'rule14_headon'


def test_c15_in_doubt_assumes_we_are_overtaking(cc):
    """C15: Rule 13(c). Inside the SOG dead-band, assume we ARE overtaking.

    We sit abaft the target's beam and are faster by 0.2 kt -- inside the AIS
    noise floor, so whether we are really gaining is genuinely unknown. 13(c)
    says assume we are, which puts us in the GIVE-WAY role. That is also the
    conservative verdict.

    The doubt must be genuine: the clause fires only for a POSITIVE
    sub-threshold differential. At exactly zero, or when the target is faster,
    we are demonstrably not coming up with her and 13(c) does not apply --
    see C4 and C15b.
    """
    assert cc.classify(own_cog=0, own_sog=10.2, tgt_cog=0, tgt_sog=10.0,
                       relative_bearing=45,
                       tgt_class='power-driven') == 'rule13_overtaking'


def test_c15b_in_doubt_never_manufactures_a_stand_on_claim(cc):
    """C15b: 13(c) biases toward give-way only.

    It is written from the overtaking vessel's perspective and creates a duty,
    not a privilege. Using it to assert stand-on would invert its purpose and
    hand the captain the dangerous verdict on doubtful data.
    """
    result = cc.classify(own_cog=90, own_sog=10.0, tgt_cog=90, tgt_sog=10.2,
                         relative_bearing=180, tgt_class='power-driven')
    assert result != 'rule13_being_overtaken', (
        '13(c) was used to claim stand-on on a sub-dead-band differential')
    assert result == 'no_situation'


def test_c16_faster_vessel_on_our_starboard_bow_is_overtaking_not_crossing(cc):
    """C16: documents the third review's second claim, which was incorrect.

    It asserted that own 000/12 kt, tgt 000/8 kt, rb 045 returns
    'rule15_giveway' and should return 'no_situation'. Neither is right:
    the code returns 'rule13_overtaking', because rb_me = 225 deg places us
    abaft the target's beam while gaining 4 kt -- which is precisely Rule
    13(b) overtaking, and we are give-way under 13(a).

    'no_situation' would have been wrong advice: a captain coming up on a
    slower vessel does have a duty to keep clear.
    """
    assert cc.classify(own_cog=0, own_sog=12, tgt_cog=0, tgt_sog=8,
                       relative_bearing=45,
                       tgt_class='power-driven') == 'rule13_overtaking'
