from facepy import GraphAPI
import datetime
from progress.bar import FillingSquaresBar
from pprint import pprint as pp
class FacebookMiner(object):
	page_fields='?fields=is_community_page,category,category_list,fan_count,hours,link,location,name,name_with_location_descriptor,overall_star_rating,parking,phone,rating_count,single_line_address,store_location_descriptor,website,were_here_count'
	def __init__(self,mine_points,API_KEY,search_rayon=1000,categories=['FOOD_BEVERAGE'],_type='place'):
		self.points=mine_points
		self.graph = GraphAPI(API_KEY,version='2.9')
		self.categories=categories
		self.r=search_rayon
		self.dim=len(self.points)
		self._type=_type
	def _mine(self,progress=True,):
		if progress:
			self.bar = FillingSquaresBar('Mining:',max=self.dim)
			for p in self.points:
				for pla in self.get_places(p):
					yield pla
				self.bar.next()
			self.bar.finish()
		else:
			for p in self.points:
				for pla in self.get_places(p):
					yield pla

	def get_places(self,p):
		c=str(p[0])+','+str(p[1])
		nearby_ids=[l['id'] for l in self.graph.search(term='',categories=str(self.categories),type=self._type,center=c,distance=self.r)['data']]
		for _id in nearby_ids:
			entity=self.graph.get(str(_id)+self.page_fields)
			entity['fb_id']=entity.pop('id')
			try:

				entity['location']['latitude']=float(entity['location'].pop('latitude'))
				entity['location']['longitude']=float(entity['location'].pop('longitude'))
			except Exception:
				pass
			try:
				entity['overall_star_rating']=float(entity.pop('overall_star_rating'))
			except Exception:
				pass
			yield entity		

class PageMiner(object):
	failed_posts=[]
	post_fields='?fields=message,name,shares,comments.limit(1).summary(1),created_time,reactions.type(LIKE).limit(0).summary(1).as(LIKE),reactions.type(WOW).limit(0).summary(1).as(WOW),reactions.type(SAD).limit(0).summary(1).as(SAD),reactions.type(LOVE).limit(0).summary(1).as(LOVE),reactions.type(ANGRY).limit(0).summary(1).as(ANGRY),reactions.type(HAHA).limit(0).summary(1).as(HAHA)'
	comment_fields='?fields=likes.limit(0).summary(1),message,comment_count,from,attachment'
	nb_posts=0
	def __init__(self,page,API_KEY,_from='',posts_ids=[]):
		self.graph = GraphAPI(API_KEY,version='2.9')
		self.name=page['name']
		self.id=page['fb_id']
		self.type=page['type']
		self.type=page['type'] 
		self._from=_from
		self.posts_ids=posts_ids if posts_ids!=[] else [u for u in self.get_posts_ids()]
		self.nb_posts=len(self.posts_ids)
	def _mine(self,post_list=[],progress=True):
		post_list=post_list if post_list!=[] else self.posts_ids
		post_bach=[{'method': 'GET', 'relative_url': p_id+self.post_fields} for p_id in post_list]
		n=len(post_list)
		posts=self.graph.batch(post_bach)
		if progress:
			bar = FillingSquaresBar('Mining %s:'%self.name, max=n)
			for post in posts:
				p=self.clean_post(post)
				if p!=None:
					yield p
				bar.next()
			bar.finish()
		else:
			for post in posts:
				p=self.clean_post(post)
				if p!=None:
					yield p	
	def parallel_mine(self):
		return None

	def get_posts_ids(self):
		if self.type=='page':
			posts_url=str(self.id)+'/posts'
		elif self.type=='group':
			posts_url=str(self.id)+'/feed'

		id_lists=self.graph.get(posts_url,page=True,limit=100,fields='id') if self._from=='' else self.graph.get(posts_url,page=True,limit=100,fields='id',since=self._from)

		for id_list in id_lists:
			for d in id_list["data"]:
				yield d['id']
	def clean_post(self,raw_post):
		post={'origin':self.id}
		post['fb_id']=raw_post['id']

		attachment=[t for t in self.attachments(raw_post['id'])]
		if attachment!=[]:
			post['attachments']=attachment
		try:
			name=raw_post['name']
		except Exception:
			pass
		else:
			if name[:11]!='Photos from':
				post['name']=name

		reactions=self.clean_reactions(raw_post)
		if reactions!=None:
			post['reactions']=reactions

		try:
			post['text']=raw_post['message']
		except:
			self.failed_posts.append(raw_post['id'])
			return None
		post['created_time']=datetime.datetime.strptime(raw_post['created_time'], '%Y-%m-%dT%H:%M:%S+0000')	
		try:
			post['#shares']=raw_post['shares']['count']
		except:
			post['#shares']=0

		comments=[c for c in self.comments(raw_post['id'])]
		if comments !=[]:
			post['comments']=comments
			post['#comments']=len(comments)
		return(post)
	def clean_reactions(self,raw_post):
		try:
			reactions={}
			for k in ['LIKE','WOW','LOVE','SAD','ANGRY','HAHA']:
				reactions[k]=raw_post[k]['summary']['total_count']
			return reactions
		except Exception as e:
			#print(str(e))
			return None 
	def comments(self,post_id):	
		comment_bach=[{'method': 'GET', 'relative_url': c_id+self.comment_fields} for c_id in self.comments_ids(post_id)]
		try:
			raw_comments=self.graph.batch(comment_bach)
			for raw_comment in raw_comments:
				c=self.clean_comment(raw_comment)
				if c!=None:
					yield c
		except Exception:
			#print ('Error in comments')
			return []
	def attachments(self,post_id):
		attachments=[]
		link_to_attachments=str(post_id)+'/attachments'
		try:
			a=self.graph.get(link_to_attachments)
			for d in a['data'][0]['subattachments']['data']:
				yield {'url':d['media']['image']['src'],'type':d['type']}
		except Exception as e:
			return []
	def clean_comment(self,raw_comment):
		try:
			comment={}
			comment['author']=raw_comment['from']
			comment['text']=raw_comment['message']
			comment['#replays']=raw_comment['comment_count']
			comment['#likes']=raw_comment['likes']['summary']['total_count']
			try:
				comment['attachment']=aw_comment['attachment']
			except Exception:
				pass
			return comment
		except Exception as e:
			#print(str(e))
			#print('Error in clean_comment: '+comment_row['id'])
			return None
	def comments_ids(self,post_id):
		link_to_comments=str(post_id)+'/comments'
		id_lists=self.graph.get(link_to_comments,page=True,limit=100,fields='id')
		for id_list in id_lists:
			for d in id_list["data"]:
				yield d['id']







