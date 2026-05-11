from dataclasses import dataclass


@dataclass(frozen=True)
class StandingsEntryDTO:
    team_id: int
    team_name: str
    matches_played: int
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int

    @property
    def wins(self) -> int:
        """Calculate wins from points (3 per win, 1 per draw)."""
        return (self.points // 3)

    @property
    def draws(self) -> int:
        """Calculate draws from points."""
        return (self.points % 3)

    @property
    def losses(self) -> int:
        """Calculate losses."""
        return max(0, self.matches_played - self.wins - self.draws)


@dataclass(frozen=True)
class GroupStandingsDTO:
    group_id: int
    group_name: str
    standings: list[StandingsEntryDTO]


@dataclass(frozen=True)
class QualifiedTeamDTO:
    team_id: int
    team_name: str
    group_id: int
    points: int
    position_in_group: int


@dataclass(frozen=True)
class TeamTournamentStatusDTO:
    team_id: int
    team_name: str
    group_id: int
    points: int
    position_in_group: int
    is_qualified_to_knockout: bool
    is_eliminated_from_tournament: bool
