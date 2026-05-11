from enum import Enum


class MatchPhase(str, Enum):
    GROUP_STAGE = "GROUP_STAGE"
    ROUND_OF_16 = "ROUND_OF_16"
    QUARTERFINAL = "QUARTERFINAL"
    SEMIFINAL = "SEMIFINAL"
    FINAL = "FINAL"
