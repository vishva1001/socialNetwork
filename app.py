import neo4j
from neo4j import GraphDatabase, basic_auth
from flask import Flask, render_template, request, redirect, url_for, flash
import networkx as nx
import os

def connect():
    driver = GraphDatabase.driver("neo4j+s://8c36a61c.databases.neo4j.io", auth=basic_auth("neo4j","SHcCzmlwObYs_BgJyxVcvT3KkyeA0A1LBkXW8Kt7z7A"))
    return driver

def sessionOpen(driver):
    session=driver.session()
    return session

def sessionClose(session):
    session.close()

def getLabels():
    driver = connect()
    session = sessionOpen(driver)
    query = '''call db.labels()'''
    piedata =""
    labels = []
    count = []
    ls=session.run(query)
    for l in ls:
        labels.append(l[0])
        query2 = "MATCH (n:"+l[0]+") return count(n) as c"
        ct = session.run(query2)
        for c in ct:
            count.append(c[0])
    sessionClose(session)
    driver.close()
    for i in range(len(labels)):
        piedata+="{x:\""+labels[i]+"\",value:"+str(count[i])+"},"
    piedata = "["+piedata[:-1]+"]"
    return labels, piedata

def getKeys():
    driver = connect()
    session = sessionOpen(driver)
    query = '''MATCH(n) WITH LABELS(n) AS labels , KEYS(n) AS keys UNWIND labels AS label UNWIND keys AS key RETURN DISTINCT label, COLLECT(DISTINCT key) AS props ORDER BY label'''
    keys = []
    ks=session.run(query)
    for k in ks:
         keys+=k[1]
    sessionClose(session)
    driver.close()
    keys=list(set(keys))
    return keys

def getGraph():
    driver = connect()
    session = sessionOpen(driver)
    query1 = '''MATCH(n) RETURN n.ID as ID'''
    allnodes = []
    ns=session.run(query1)
    allrels=""
    nodes=""
    for n in ns:
        allnodes.append(n['ID']) 
        nodes+="{\"id\":\""+n['ID']+"\"},"
        query2 = "MATCH (a {ID: '"+n['ID']+"'})-[r]-(b) RETURN b.ID as ID"
        rels = session.run(query2)
        for r in rels:
            allrels+="{\"from\":\""+n['ID']+"\",\"to\":\""+r['ID']+"\"},"
    sessionClose(session)
    driver.close()
    edges = "\"edges\":["+allrels[:-1]+"]"
    nodes = "\"nodes\":["+nodes[:-1]+"]"
    graphstring = "{"+nodes+","+edges+"}"
    return allnodes, graphstring

def getResults(label, key, value, match):
    driver = connect()
    session = sessionOpen(driver)

    if label and not key and value=="":
        queryId = '''MATCH (n:'''+label+''') return n.ID as ID'''
    elif key and value=="" and not label:
        queryId = "MATCH (p) WHERE any(key in keys(p) WHERE key='"+key+"') RETURN p.ID as ID"
    elif value!="" and not key and not label:
        if match == "fuzzy":
            queryId = "MATCH (p) WHERE any(key in keys(p) WHERE apoc.text.fuzzyMatch(p[key], '"+value+"')) RETURN p.ID as ID"
        else:
            queryId = "MATCH (p) WHERE any(key in keys(p) WHERE p[key] = '"+value+"') RETURN p.ID as ID"
    elif key and value!="" and not label:
        if match == "fuzzy":
            queryId = "MATCH (n) WHERE apoc.text.fuzzyMatch(n."+key+",'"+value+"') RETURN n.ID as ID"
        else:
            queryId = "MATCH (n {"+key+":'"+value+"'}) return n.ID as ID"
    elif key and label and value=="":
        queryId = "MATCH (p:"+label+") WHERE any(key in keys(p) WHERE key = '"+key+"') RETURN p.ID as ID"
    elif value!="" and label and not key:
        if match == "fuzzy":
            queryId = "MATCH (p:"+label+") WHERE any(key in keys(p) WHERE apoc.text.fuzzyMatch(p[key],'"+value+"')) RETURN p.ID as ID"
        else:
            queryId = "MATCH (p:"+label+") WHERE any(key in keys(p) WHERE p[key] = '"+value+"') RETURN p.ID as ID"
    else:
        if match == "fuzzy":
            queryId = "MATCH (n:"+label+") where  apoc.text.fuzzyMatch(n."+key+",'"+value+"') return n.ID as ID"
        else:
            queryId = "MATCH (n:"+label+" {"+key+":'"+value+"'}) return n.ID as ID"
    results = session.run(queryId)
    res = []
    for r in results:
        res.append(r['ID'])   
    sessionClose(session)
    driver.close()
    return res

def getNodeInfo(results):
    driver = connect()
    session = sessionOpen(driver)
    properties=[]
    relations=[]
    for r in results:
        str1 = ""
        str2 = ""
        query1 = "MATCH (n {ID:'"+r+"'}) UNWIND keys(n) AS key RETURN key, n[key] as value"
        query2 = "MATCH (a {ID: '"+r+"'})-[r]-(b) RETURN type(r) as R, b.ID as ID"
        props=session.run(query1)
        rels = session.run(query2)
        for p in props:
            str1+=p['key']+":"+p['value']+", "
        properties.append(str1[:-2])
        for rel in rels:
            str2+=rel['R']+" : "+rel['ID']+", "
        relations.append(str2[:-2])
    sessionClose(session)
    driver.close()
    return properties, relations

def getCliques(nodes):
    clqs=[]
    driver = connect()
    session = sessionOpen(driver)
    file1 = open("edgelist.txt","w")
    for n in nodes:
        query = "MATCH (a {ID: '"+n+"'})-[r]-(b) RETURN b.ID as ID"
        ids = session.run(query)
        for id in ids:
            file1.write(n+","+id['ID']+"\n")
    file1.close()
    sessionClose(session)
    driver.close()
    G = nx.read_edgelist("edgelist.txt",delimiter=',')
    for clq in nx.clique.find_cliques(G):
        if len(clq)>2:
            clqs.append(clq)
    return clqs

app = Flask(__name__)
print(os.environ['NEO4J_DB'])

@app.route("/")
def index():
        return redirect(url_for('search'))

@app.route("/search", methods=['GET'])
def search():   
    label = request.args.get('label')
    key = request.args.get('key')
    value = request.args.get('value')
    match = request.args.get('match')
    labels, piedata =getLabels()
    keys=getKeys()
    nodes, graphstring=getGraph()
    cliques = getCliques(nodes) 

    if not value:
        value=""
    if label is None and value=="" and key is None:
        return render_template('search.html', nodes=nodes, labels=labels, keys=keys, cliques=cliques, graphstring=graphstring, piedata=piedata)
    else:
        results = getResults(label, key, value, match)
        properties, relations = getNodeInfo(results)
        return render_template('search.html', nodes=nodes, labels=labels, keys=keys, res=results, props=properties, rels=relations, cliques=cliques, graphstring=graphstring, piedata=piedata)
