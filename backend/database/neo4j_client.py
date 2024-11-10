from neo4j import GraphDatabase
from config import settings

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def create_user_preference(self, user_id: str, entity: str, relationship: str, value: str):
        with self.driver.session() as session:
            query = """
            MERGE (u:User {id: $user_id})
            MERGE (e:Entity {name: $entity})
            MERGE (u)-[r:HAS_PREFERENCE {type: $relationship}]->(e)
            SET r.value = $value
            """
            session.run(query, user_id=user_id, entity=entity, 
                       relationship=relationship, value=value)

    def get_user_preferences(self, user_id: str):
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})-[r:HAS_PREFERENCE]->(e:Entity)
            RETURN e.name as entity, r.type as relationship, r.value as value
            """
            result = session.run(query, user_id=user_id)
            return [dict(record) for record in result]

    def store_itinerary(self, user_id: str, city: str, places: list):
        with self.driver.session() as session:
            query = """
            MERGE (u:User {id: $user_id})
            MERGE (c:City {name: $city})
            WITH u, c
            UNWIND $places as place
            MERGE (p:Place {name: place})
            MERGE (u)-[:VISITED]->(p)
            MERGE (p)-[:LOCATED_IN]->(c)
            """
            session.run(query, user_id=user_id, city=city, places=places)
