from datetime import datetime, timedelta

from server.db.models import TripSurvey, Statistics


def close_survey(survey: TripSurvey):
    # TODO: run as cron job each day
    if survey:
        stats = Statistics()
        stats.tripsCount = len(survey.trips)
        stats.tripsVoted = sum(list(map(lambda item: 1 if len(item.votes) > 0 else 0, survey.trips)))
        stats.votePointsGiven = sum(list(map(lambda t: sum(list(map(lambda vote: vote.points, t.votes))), survey.trips)))
        stats.lengthInDays = abs((datetime.fromtimestamp(survey.createdAt) - datetime.now()).days)

        survey.update(set__openUntil=datetime.utcnow() - timedelta(days=1), set__statistics=stats)
