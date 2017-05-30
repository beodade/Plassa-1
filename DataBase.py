import pymongo
'''3 collections de documents dans la db Plassa 
1-gplaces: collection de google Api Places 
2-Pages: cllection de page/group facebook 
3-Posts :collections de posts sur des pages 

'''

def get_db(user,pwd):
	''' connect to the db '''
	client = pymongo.MongoClient('mongodb://'+user+':'+pwd+'@plassacluster-shard-00-00-5zy4i.mongodb.net:27017,plassacluster-shard-00-01-5zy4i.mongodb.net:27017,plassacluster-shard-00-02-5zy4i.mongodb.net:27017/Plassa?ssl=true&replicaSet=PlassaCluster-shard-0&authSource=admin')
	return client.Plassa
def get_duplicates(field_name,coll_name,db):
	''' get all the docs with the same field value:
		ex: tout les docs qui ont le meme name
		a ne pas confondre field_name avec field_value !!!!!
	'''
	duplicat_pipline=[{ '$group': {'_id': { field_name: "$"+field_name },'count': { '$sum':  1 },'docs': { '$push': "$_id" }}},{'$match': {'count': { '$gt' : 1 }}}]
	coll=getattr(db, coll_name)
	return coll.aggregate(duplicat_pipline)
