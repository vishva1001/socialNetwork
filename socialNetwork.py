import neo4j
from neo4j import GraphDatabase, basic_auth
import pandas as pd
import os

#connect to neo4j aura
driver = GraphDatabase.driver(os.environ['NEO4J_DB'], auth=basic_auth(os.environ['NEO4J_USR'],['NEO4J_PWD']))

#trim spaces from dataset
def trim(dataset):
    trim = lambda x: x.strip() if type(x) is str else x
    return dataset.applymap(trim)

eptxt="/home/ubuntu/static/entity_properties.txt"
ertxt="/home/ubuntu/static/entity_relationships.txt"
epcsv="/home/ubuntu/static/entity_properties.csv"
ercsv="/home/ubuntu/static/entity_relationships.csv"

#text to csv
read_file = trim(pd.read_csv(eptxt, delimiter='\t', skipinitialspace = True ))
read_file.to_csv(epcsv, index=False)
read_file2 = trim(pd.read_csv(ertxt, delimiter='\t', skipinitialspace = True))
read_file2.to_csv(ercsv, index=False)

#new database session
session=driver.session()
#clear any existing data
session.run('match (n) detach delete (n)')

#Load entities and properties
df = pd.read_csv(epcsv)
header=list(df.columns)
for ind in df.index:
    session.run("MERGE (a {"+header[0]+":'"+df[header[0]][ind]+"'}) on match set a."+df[header[1]][ind]+"='"+df[header[2]][ind]+"' on create set a."+df[header[1]][ind]+"='"+df[header[2]][ind]+"'")

#Load label and relationships
df = pd.read_csv(ercsv)
header=list(df.columns)
for ind in df.index:
    session.run("MATCH (n {ID:'"+df[header[1]][ind]+"'}) set n:"+df[header[2]][ind])
    session.run("MATCH (n {ID:'"+df[header[3]][ind]+"'}) set n:"+df[header[4]][ind])
    session.run("MATCH (a {ID:'"+df[header[1]][ind]+"'}), (b {ID:'"+df[header[3]][ind]+"'}) create (a)-[r:"+df[header[0]][ind]+"]->(b) return(type(r))")

session.close()
driver.close()
