from datetime import date

try:
    from src.domain.exceptions.validation_error import ValidationError
    from src.dto.match_queries import MatchesByStadiumDTO
    from src.dto.player_queries import (
        MostExpensivePlayerByConfederationDTO,
        UnderTwentyOnePlayersByTeamDTO,
    )
    from src.dto.team_queries import MostExpensiveTeamByHostCountryDTO
    from src.repositories.query_repository import QueryRepository
except ModuleNotFoundError:
    from domain.exceptions.validation_error import ValidationError
    from dto.match_queries import MatchesByStadiumDTO
    from dto.player_queries import (
        MostExpensivePlayerByConfederationDTO,
        UnderTwentyOnePlayersByTeamDTO,
    )
    from dto.team_queries import MostExpensiveTeamByHostCountryDTO
    from repositories.query_repository import QueryRepository


class QueryService:
    def __init__(self, query_repository: QueryRepository) -> None:
        self._query_repository = query_repository

    def get_most_expensive_player_by_confederation(
        self,
    ) -> list[MostExpensivePlayerByConfederationDTO]:
        return self._query_repository.get_most_expensive_player_by_confederation()

    def get_matches_by_stadium(self, stadium_id: int) -> list[MatchesByStadiumDTO]:
        if stadium_id <= 0:
            raise ValidationError("Stadium id must be greater than zero.")

        return self._query_repository.get_matches_by_stadium(stadium_id)

    def get_most_expensive_team_by_host_country(
        self,
    ) -> list[MostExpensiveTeamByHostCountryDTO]:
        return self._query_repository.get_most_expensive_team_by_host_country()

    def get_under_twenty_one_players_by_team(
        self,
        reference_date: date,
    ) -> list[UnderTwentyOnePlayersByTeamDTO]:
        if reference_date is None:
            raise ValidationError("Reference date is required.")

        return self._query_repository.get_under_twenty_one_players_by_team(reference_date)
