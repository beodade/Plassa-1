import matplotlib.path as mplPath
from numpy import mgrid,where,array
from googleplaces import GooglePlaces, types, lang
from progress.bar import FillingSquaresBar
class GoogleMiner(object):
	failed_places=[]
	def __init__(self,grid,API_KEY,r=None,place_type=[types.TYPE_RESTAURANT],searcher='radar'):
		self.api = GooglePlaces(API_KEY)
		self.grid=grid
		self.r=int(0.564*haversine(0,0,0,grid.step)) if r==None else r
		self.searcher=self.api.radar_search if searcher=='radar' else self.api.nearby_search
		self.place_type=place_type
	def _mine(self,progress=True):
		if progress:
			bar = FillingSquaresBar('Mining %s:'%self.grid.name, max=self.grid.dim)
			for i in range(self.grid.dim):
				p={'lat':self.grid.points[i][0],'lng':self.grid.points[i][1]}
				query_result = self.searcher(lat_lng=p,
					radius=self.r, types=self.place_type)
				for place in self.get_places(query_result):
					yield(place)
				bar.next()
			bar.finish()
		else:
			for i in range(dim):
				p={'lat':self.grid.points[i][0],'lng':self.grid.points[i][1]}
				query_result = self.searcher(lat_lng=p,
					radius=self.r, types=self.place_type)
				for place in self.get_places(query_result):
					yield(place)
	def get_places(self,query_result):
		for place in query_result.places:
			try:
				place.get_details()
				gplace=dict(place.details)
				gplace.pop('scope', None)
				gplace.pop('vicinity', None)
				gplace.pop('utc_offset', None)
				gplace.pop('reference', None)
				gplace.pop('international_phone_number', None)
				gplace.pop('id', None)
				gplace.pop('icon', None)
				gplace.pop('adr_address', None)
				gplace.pop('address_components', None)
				geo=gplace.pop('geometry', None)['location']
				gplace['geo']=geo
				geo['lat']=float(geo['lat'])
				geo['lng']=float(geo['lng'])
				try:
					gplace['rating']=float(gplace['rating'])
				except:
					gplace['rating']=None
				photos=[]
				for p in place.photos:
					p.get(maxheight=4000)
					photos.append(p.url)
				gplace['photos']=photos
				yield gplace
			except Exception as e :
				self.failed_places.append(gplace['name'])
class Grid(object):
	def __init__(self,Border,step,name='Alger'):
		self.name=name
		self.border=Border
		self.step=step
		self.limit_lat=(min(Border[:,0]),max(Border[:,0]))
		self.limit_long=(min(Border[:,1]),max(Border[:,1]))	
		self.brut=mgrid[self.limit_lat[0]:self.limit_lat[1]:self.step, self.limit_long[0]:self.limit_long[1]:self.step].reshape(2,-1).T
		bbPath = mplPath.Path(Border)
		self.points=self.brut[where(bbPath.contains_points(self.brut))]
		self.dim=len(self.points)
	def filter(self,polygone):
		bbPath = mplPath.Path(polygone)
		self.points=self.points[where(bbPath.contains_points(self.points))]