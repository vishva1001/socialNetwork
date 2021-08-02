import neo4j
from neo4j import GraphDatabase, basic_auth
import pandas as pd

#connect to neo4j sandbox
#driver = GraphDatabase.driver("bolt://3.238.152.123:7687", auth=basic_auth("neo4j", "striker-twists-bearing"))
driver = GraphDatabase.driver("neo4j+s://8c36a61c.databases.neo4j.io", auth=basic_auth("neo4j","SHcCzmlwObYs_BgJyxVcvT3KkyeA0A1LBkXW8Kt7z7A"))
#query
cypher_query = '''
MATCH (movie:Movie)<-[:DIRECTED]-(p:Person {name:'Nora Ephron'})
 RETURN movie.title as title'''

#new session
'''session = driver.session()
results = session.run(cypher_query)
for record in results:
  print(record['title'])
session.close()
#session closed
'''

#trim spaces
def trim(dataset):
    trim = lambda x: x.strip() if type(x) is str else x
    return dataset.applymap(trim)
#text to csv
read_file = trim(pd.read_csv('/home/ubuntu/static/entity_properties.txt', delimiter='\t', skipinitialspace = True ))
read_file.to_csv('/home/ubuntu/static/entity_properties.csv', index=False)
read_file2 = trim(pd.read_csv('/home/ubuntu/static/entity_relationships.txt', delimiter='\t', skipinitialspace = True))
read_file2.to_csv('/home/ubuntu/static/entity_relationships.csv', index=False)

'''#trim extra spaces
with open("entity_properties.csv") as infile:
    reader=csv.DictReader(infile)
    fieldnames=reader.fieldnames
    with open("xyz.csv", "w") as wr:
        writer = csv.DictWriter(wr, fieldnames=fieldnames)
        for row in reader:
            row.update({fieldname: value.strip() for (fieldname, value) in row.items()})
            print({fieldname: value.strip() for (fieldname, value) in row.items()})
            writer.writerow(row)
'''
#new session
session=driver.session()
session.run('match (n) detach delete (n)')
df = pd.read_csv('/home/ubuntu/static/entity_properties.csv')
header=list(df.columns)
#Enter entities and properties
for ind in df.index:
    result=session.run("MERGE (a {"+header[0]+":'"+df[header[0]][ind]+"'}) on match set a."+df[header[1]][ind]+"='"+df[header[2]][ind]+"' on create set a."+df[header[1]][ind]+"='"+df[header[2]][ind]+"'")
'''
for ind in df.index:
    if df[header[1]][ind]=="Phone":
        result = session.run("MATCH (n:Person {ID:'"+df[header[0]][ind]+"'}) return n.Phone as Phone")
        for record in result:
            print(record)
            if record['Phone'] is None:
                #print("do this")
                result=session.run("MERGE (a {"+header[0]+":'"+df[header[0]][ind]+"'}) on match set a."+df[header[1]][ind]+"='"+df[header[2]][ind]+"' on create set a."+df[header[1]][ind]+"='"+df[header[2]][ind]+"'")
            else:
                result=session.run("MERGE (a {"+header[0]+":'"+df[header[0]][ind]+"'}) on match set a."+df[header[1]][ind]+"=[a.Phone,'"+df[header[2]][ind]+"'] on create set a."+df[header[1]][ind]+"=[a.Phone,'"+df[header[2]][ind]+"']")
    else:
        result=session.run("MERGE (a {"+header[0]+":'"+df[header[0]][ind]+"'}) on match set a."+df[header[1]][ind]+"='"+df[header[2]][ind]+"' on create set a."+df[header[1]][ind]+"='"+df[header[2]][ind]+"'")
'''

#Enter label and relationships
df = pd.read_csv('/home/ubuntu/static/entity_relationships.csv')
header=list(df.columns)
for ind in df.index:
    result=session.run("MATCH (n {ID:'"+df[header[1]][ind]+"'}) set n:"+df[header[2]][ind])
    result=session.run("MATCH (n {ID:'"+df[header[3]][ind]+"'}) set n:"+df[header[4]][ind])
    result=session.run("MATCH (a {ID:'"+df[header[1]][ind]+"'}), (b {ID:'"+df[header[3]][ind]+"'}) create (a)-[r:"+df[header[0]][ind]+"]->(b) return(type(r))")
    #if df[header[3]][ind]=='Person' and df[header[5]][ind]=='Person':
        #result=session.run("MATCH (a {ID:'"+df[header[1]][ind]+"'}), (b {ID:'"+df[header[3]][ind]+"'}) create (b)-[r:"+df[header[0]][ind]+"]->(a) return(type(r))")
session.close()
driver.close()
