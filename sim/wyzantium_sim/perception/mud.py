"""D-023 interim mud-degradation model (until MR-001).

Committed form: P(detect | mud fraction f) = P_mask(f) * max(0, 1 - f/f_c),
f_c swept {0.6, 0.8, 1.0} (#41). P_mask is "the clean-mask literature
curve"; the 2026-08-02 corpus pass found no text-sourced numeric masking
curve (figure-only), so prior_v1 uses P_mask(f) = 1 - f — the visible-area
fraction — labeled EXT per the corpus's own gap list. MR-001 replaces this
via the curve-swap protocol.
"""


def detection_factor(mud_fraction, f_c):
    f = float(mud_fraction)
    p_mask = 1.0 - f
    return max(0.0, p_mask) * max(0.0, 1.0 - f / float(f_c))
