try:
    from src.dto.standings_models import (
        GroupStandingsDTO,
        QualifiedTeamDTO,
        StandingsEntryDTO,
        TeamTournamentStatusDTO,
    )
    from src.repositories.standings_repository import StandingsRepository
    from src.repositories.match_repository import MatchRepository
except ModuleNotFoundError:
    from dto.standings_models import (
        GroupStandingsDTO,
        QualifiedTeamDTO,
        StandingsEntryDTO,
        TeamTournamentStatusDTO,
    )
    from repositories.standings_repository import StandingsRepository
    from repositories.match_repository import MatchRepository


class StandingsService:
    def __init__(
        self,
        standings_repository: StandingsRepository,
        match_repository: MatchRepository,
    ) -> None:
        self._standings_repository = standings_repository
        self._match_repository = match_repository

    def get_group_standings(self, group_id: int) -> GroupStandingsDTO:
        """Get standings for a specific group."""
        standings_data = self._standings_repository.get_group_standings(group_id)

        standings_entries = [
            StandingsEntryDTO(
                team_id=row["team_id"],
                team_name=row["team_name"],
                matches_played=row["matches_played"] or 0,
                points=row["points"] or 0,
                goals_for=row["goals_for"] or 0,
                goals_against=row["goals_against"] or 0,
                goal_difference=(row["goals_for"] or 0) - (row["goals_against"] or 0),
            )
            for row in standings_data
        ]

        return GroupStandingsDTO(
            group_id=group_id,
            group_name=f"Group {chr(64 + group_id)}",
            standings=standings_entries,
        )

    def get_all_group_standings(self) -> list[GroupStandingsDTO]:
        """Get standings for all groups."""
        all_standings = []
        for group_id in range(1, 13):
            all_standings.append(self.get_group_standings(group_id))
        return all_standings

    def get_qualified_teams(self, limit_per_group: int = 2) -> list[QualifiedTeamDTO]:
        """Get qualified teams (top N from each group)."""
        qualified_data = self._standings_repository.get_all_qualified_teams(limit_per_group)

        qualified_teams = [
            QualifiedTeamDTO(
                team_id=row["team_id"],
                team_name=row["team_name"],
                group_id=row["group_id"],
                points=row["points"] or 0,
                position_in_group=self._get_position_in_group(
                    row["group_id"], row["team_id"], qualified_data, limit_per_group
                ),
            )
            for row in qualified_data
        ]

        return qualified_teams

    def get_group_stage_team_statuses(self, limit_per_group: int = 2) -> list[TeamTournamentStatusDTO]:
        """Return each grouped team's tournament outcome after the group stage."""
        statuses = []

        for group_id in range(1, 13):
            group_standings = self.get_group_standings(group_id)
            for position, entry in enumerate(group_standings.standings, start=1):
                is_qualified = position <= limit_per_group
                statuses.append(
                    TeamTournamentStatusDTO(
                        team_id=entry.team_id,
                        team_name=entry.team_name,
                        group_id=group_id,
                        points=entry.points,
                        position_in_group=position,
                        is_qualified_to_knockout=is_qualified,
                        is_eliminated_from_tournament=not is_qualified,
                    )
                )

        return statuses

    def calculate_standings_after_match(self, match_id: int) -> None:
        """Recalculate standings after a match result is saved."""
        match_data = self._match_repository.find_by_id(match_id)
        if not match_data or not self._match_repository.has_result(match_id):
            return

        group_id = match_data.get("group_id")
        if group_id:
            standings = self.get_group_standings(group_id)
            for entry in standings.standings:
                self._standings_repository.create_standings_record(
                    team_id=entry.team_id,
                    group_id=group_id,
                    matches_played=entry.matches_played,
                    points=entry.points,
                    goals_for=entry.goals_for,
                    goals_against=entry.goals_against,
                )

    def _get_position_in_group(
        self,
        group_id: int,
        team_id: int,
        qualified_data: list[dict],
        limit: int,
    ) -> int:
        """Get the position of a team within its group in qualified list."""
        position = 1
        for row in qualified_data:
            if row["group_id"] == group_id:
                if row["team_id"] == team_id:
                    return position
                position += 1
        return position

    def create_knockout_brackets(self) -> dict:
        """Create knockout brackets from qualified teams."""
        qualified = self.get_qualified_teams(2)

        groups = {}
        for team in qualified:
            if team.group_id not in groups:
                groups[team.group_id] = []
            groups[team.group_id].append(team)

        brackets = {}
        group_list = sorted(groups.keys())

        for i in range(0, len(group_list), 2):
            if i + 1 < len(group_list):
                group1 = group_list[i]
                group2 = group_list[i + 1]

                if len(groups[group1]) >= 1 and len(groups[group2]) >= 1:
                    match_number = (i // 2) + 1
                    brackets[f"R16_Match_{match_number}_A"] = {
                        "home": groups[group1][0],
                        "away": groups[group2][0],
                    }
                if len(groups[group1]) >= 2 and len(groups[group2]) >= 2:
                    match_number = (i // 2) + 1
                    brackets[f"R16_Match_{match_number}_B"] = {
                        "home": groups[group1][1],
                        "away": groups[group2][1],
                    }

        return brackets
