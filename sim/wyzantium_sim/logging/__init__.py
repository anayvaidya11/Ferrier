"""T8 trial logging (PHASE1_PLAN §2: logging/trial_logger.py).

Named per the committed plan; as a subpackage this never shadows the
stdlib — a bare `import logging` anywhere still resolves to the standard
library under Python 3 absolute imports. Only the spelled-out
`from wyzantium_sim import logging` reaches this package.
"""
