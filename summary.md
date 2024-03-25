# Course 1: About the Driver

# Import the neo4j dependency
from neo4j import GraphDatabase

# Create a new Driver instance
# Replace "neo4j://localhost:7687" with the actual connection string
# Replace "neo4j" with the actual username and "neo" with the actual password
# Ensure to replace these placeholders with the actual values for your Neo4j instance
with GraphDatabase.driver(
    "neo4j://localhost:7687",  # (1) Connection string
    auth=("neo4j", "neo")       # (2) Authentication details (username, password)
) as driver:
    # Execute code before the driver graciously closes itself
    pass

# Verify the connection details
driver.verify_connectivity()



------------------------------------------------------------------------------------------------------------------



# Course 2: Connection Strings and Authentication

# Creating a Driver Instance
# Replace "connectionString" with the actual connection string
# Replace "username" with the actual username and "password" with the actual password
# Replace **configuration with any additional configuration parameters
driver = GraphDatabase.driver(
    "connectionString",         # (1) Connection string
    auth=("username", "password"),  # (2) Authentication details (username, password)
    **configuration             # (3) Additional configuration parameters
)



------------------------------------------------------------------------------------------------------------------



# Course 3: Challenge: Adding the Driver
# Modify the init_driver() function in api/neo4j.py
# Install the neo4j dependency
# Import the neo4j dependency
# from neo4j import GraphDatabase

# Create an instance of the driver
# current_app.driver = GraphDatabase.driver(uri, auth=(username, password))
# Verify Connectivity
# current_app.driver.verify_connectivity()



------------------------------------------------------------------------------------------------------------------



# Course 4: Sessions and Transactions

# Open a new Session
with driver.session() as session:
    pass

# Running a Read Transaction
# Define the get_movies() function to run within a Read Transaction
def get_movies(tx, title):
    return tx.run("""
        MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
        WHERE m.title = $title
        RETURN p.name AS name
        LIMIT 10
    """, title=title)

# Execute get_movies within a Read Transaction
session.execute_read(get_movies,
    title="Arthur"
)

# Running a Write Transaction
# Define the create_person() function to run within a Write Transaction
def create_person(tx, name):
    return tx.run(
        "CREATE (p:Person {name: $name})",
        name=name
    )

# Execute the `create_person` function within a Write Transaction
session.execute_write(create_person, name="Michael")



------------------------------------------------------------------------------------------------------------------



# Course 5: Processing Results

# Get Actors by Movie title
# Define the get_actors() function to retrieve actors by movie title
def get_actors(tx, movie): # (1)
    result = tx.run("""
        MATCH (p:Person)-[:ACTED_IN]->(:Movie {title: $title})
        RETURN p
    """, title=movie)

    # Access the `p` value from each record
    return [ record["p"] for record in result ]

# Open a Session
with driver.session() as session:
    # Run the unit of work within a Read Transaction
    actors = session.execute_read(get_actors, movie="The Green Mile") # (2)

    # Print each actor
    for record in actors:
        print(record["p"])

    session.close()



------------------------------------------------------------------------------------------------------------------



# Course 6: The Neo4j Type System

# Working with Node Objects
# Accessing properties of a Node object
node = record["movie"]
print(node.id)              # (1) Access the internal ID of the node
print(node.labels)          # (2) Access the labels attributed to the node
print(node.items())         # (3) Access all properties of the node
print(node["name"])         # Access a specific property using bracket notation
print(node.get("name", "N/A")) # Access a specific property using get() with a default value

# Working with Relationship Objects
# Accessing properties of a Relationship object
acted_in = record["actedIn"]
print(acted_in.id)         # (1) Access the internal ID of the relationship
print(acted_in.type)       # (2) Access the type of the relationship
print(acted_in.items())    # (3) Access all properties of the relationship
print(acted_in["roles"])   # Access a specific property using bracket notation
print(acted_in.get("roles", "(Unknown)")) # Access a specific property using get() with a default value
print(acted_in.start_node) # (5) Access the start node of the relationship
print(acted_in.end_node)   # (6) Access the end node of the relationship

# Working with Path Objects
# Accessing properties of a Path object
path = record["path"]
print(path.start_node)      # (1) Access the start node of the path
print(path.end_node)        # (2) Access the end node of the path
print(len(path))            # (3) Get the number of relationships in the path
print(path.relationships)  # (4) Access all relationships in the path


# Path Segments
# A path is split into segments representing each relationship in the path. 
# For example, say we have a path of (p:Person)-[:ACTED_IN]->(m:Movie)-[:IN_GENRE]->(g:Genre), there would be two relationships.
# The relationships within a path can be iterated over using the iter() function.

# Iterating over Segments
for rel in iter(path):
    print(rel.type)         # Access the type of the relationship (str)
    print(rel.start_node)   # Access the start node of the relationship (int)
    print(rel.end_node)     # Access the end node of the relationship (int)


# Temporal Data Types
# Temporal data types are implemented by the neo4j.time module.
# It provides a set of types compliant with ISO-8601 and Cypher, which are similar to those found in the built-in datetime module. 
# Sub-second values are measured to nanosecond precision and the types are compatible with pytz.

# Create a DateTime instance using individual values
datetime = neo4j.time.DateTime(year, month, day, hour, minute, second, nanosecond)

# Create a DateTime from a time stamp (seconds since unix epoch).
from_timestamp = neo4j.time.DateTime(1609459200000) # 2021-01-01

# Get the current date and time.
now = neo4j.time.DateTime.now()

print(now.year) # 2022


# Spatial Data Types
# Cypher has built-in support for handling spatial values (points), and the underlying database supports storing these point values as properties on nodes and relationships.

# Points
# Cypher Type    Python Type
# Point          neo4j.spatial.Point
# Point (Cartesian) neo4j.spatial.CartesianPoint
# Point (WGS-84) neo4j.spatial.WGS84Point

# CartesianPoint
# A Cartesian Point can be created in Cypher by supplying x and y values to the point() function. 
# The optional z value represents the height.
# To create a Cartesian Point in Python, you can import the neo4j.spatial.CartesianPoint class.
# Using X and Y values
twoD = CartesianPoint((1.23, 4.56))
print(twoD.x, twoD.y)

# Using X, Y and Z
threeD = CartesianPoint((1.23, 4.56, 7.89))
print(threeD.x, threeD.y, threeD.z)

# WGS84Point
# A WGS84 Point can be created in Cypher by supplying latitude and longitude values to the point() function. 
# To create a Cartesian Point in Python, you can import the neo4j.spatial.WGS84Point class.
london = WGS84Point((-0.118092, 51.509865))
print(london.longitude, london.latitude)

the_shard = WGS84Point((-0.086500, 51.504501, 310))
print(the_shard.longitude, the_shard.latitude, the_shard.height)

# Distance
# When using the point.distance function in Cypher, the distance calculated between two points is returned as a float.
# Example:
# Run
# WITH point({x: 1, y:1}) AS one,
#      point({x: 10, y: 10}) AS two
# RETURN point.distance(one, two) // 12.727922061357855



------------------------------------------------------------------------------------------------------------------



# Course 7: Handling Driver Errors

## Exception Types

When executing a Cypher statement, various exceptions may arise. These exceptions are categorized based on their nature:

- `neo4j.exceptions.Neo4jError`: Raised when the Cypher engine returns an error to the client.
- `neo4j.exceptions.ClientError`: Raised when the client sends a bad request, with potential for successful outcome upon request modification.
- `neo4j.exceptions.CypherSyntaxError`: Raised when the Cypher statement contains syntax errors.
- `neo4j.exceptions.CypherTypeError`: Raised when one or more data types in the query are incorrect.
- `neo4j.exceptions.ConstraintError`: Raised when an action is rejected due to a constraint violation.
- `neo4j.exceptions.AuthError`: Raised when authentication failure occurs.
- `neo4j.exceptions.Forbidden`: Raised when the action is forbidden for the authenticated user.
- `neo4j.exceptions.TransientError`: Raised when the database cannot service the request immediately, with potential success upon retry.
- `neo4j.exceptions.ForbiddenOnReadOnlyDatabase`: Raised when attempting to run write Cypher on a read-only database.
- `neo4j.exceptions.NotALeader`: Raised when a write query cannot be executed on the current server because it is not the leader of the cluster.

## Handling Exceptions

You can handle specific exceptions using a try/catch block or catch all `Neo4jErrors` instances:

<!-- ```python
from neo4j.exceptions import Neo4jError, ConstraintError

try:
    tx.run(cypher, params)
except ConstraintError as err:
    print("Handle constraint violation")
    print(err.code)     # Error code
    print(err.message)  # Error message
except Neo4jError as err:
    print("Handle generic Neo4j Error")
    print(err.code)     # Error code
    print(err.message)  # Error message -->

## Error Codes

Each Neo4jError includes a code property, providing higher-level information about the query. Error codes follow the format Neo.[Classification].[Category].[Title], where:

- Classification: High-level classification of the error (e.g., client-side error, database error).
- Category: Higher-level category for the error (e.g., clustering, procedure, schema).
- Title: Specific information about the error.
- For a comprehensive list of status codes, refer to the Neo4j Documentation on Status Codes.

This summary provides an overview of handling driver errors in Neo4j Python Driver, including exception types, handling mechanisms, and error codes, presented in Markdown format.



------------------------------------------------------------------------------------------------------------------



