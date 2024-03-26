from api.data import ratings
from api.exceptions.notfound import NotFoundException

from api.data import goodfellas


class RatingDAO:
    """
    The constructor expects an instance of the Neo4j Driver, which will be
    used to interact with Neo4j.
    """
    def __init__(self, driver):
        self.driver=driver

    """
    Add a relationship between a User and Movie with a `rating` property.
    The `rating` parameter should be converted to a Neo4j Integer.
    """
    # tag::add[]
    def add(self, user_id, movie_id, rating):
        #
        # Create function with a query to save the rating in the database
        def create_rating(tx, user_id, movie_id, rating):
            return tx.run("""
            MATCH (u:User {userId: $user_id})
            MATCH (m:Movie {tmdbId: $movie_id})
            MERGE (u)-[r:RATED]->(m)
            SET r.rating = $rating,
                r.timestamp = timestamp()
            RETURN m {
                .*,
                rating: r.rating
            } AS movie
            """, user_id=user_id, movie_id=movie_id, rating=rating).single()

        #starting a session with a write execution to write into the database
        with self.driver.session() as session:
            record = session.execute_write(create_rating, user_id=user_id, movie_id=movie_id, rating=rating)

        #if the record is None, it means the movie does not exist in our database (won't happen as the movie that are in the website are in fact in the data base but we need to handle the error anyway)
        if record is None:
                raise NotFoundException()

        #we return the records from the query (all information about the movie + the movie rating from the relationship)
        return record["movie"]

    """
    Return a paginated list of reviews for a Movie.

    Results should be ordered by the `sort` parameter, and in the direction specified
    in the `order` parameter.
    Results should be limited to the number passed as `limit`.
    The `skip` variable should be used to skip a certain number of rows.
    """
    # tag::forMovie[]
    def for_movie(self, id, sort = 'timestamp', order = 'ASC', limit = 6, skip = 0):
        # Get ratings for a Movie
        def get_movie_ratings(tx, id, sort, order, limit):
            cypher = """
            MATCH (u:User)-[r:RATED]->(m:Movie {{tmdbId: $id}})
            RETURN r {{
                .rating,
                .timestamp,
                user: u {{
                    .userId, .name
                }}
            }} AS review
            ORDER BY r.`{0}` {1}
            SKIP $skip
            LIMIT $limit
            """.format(sort, order)

            result = tx.run(cypher, id=id, limit=limit, skip=skip)

            return [ row.get("review") for row in result ]

        with self.driver.session() as session:
            return session.execute_read(get_movie_ratings, id, sort, order, limit)
    # end::forMovie[]
