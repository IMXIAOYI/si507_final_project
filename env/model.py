import json
import secret
import requests
import sqlite3
from bs4 import BeautifulSoup

city_name="Seattle"
CACHE_FNAME='cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}


def init(name):
	global city_name
	city_name=name
	conn = sqlite3.connect('final507.sqlite')
	cur = conn.cursor()
	statement = '''
	DROP TABLE IF EXISTS 'restaurants_info';
	'''
	cur.execute(statement)
	statement = '''
	DROP TABLE IF EXISTS 'city_info';
	'''
	cur.execute(statement)
	conn.commit()
	statement = '''
	CREATE TABLE 'restaurants_info' (
	'id' TEXT PRIMARY KEY,
	'name' TEXT,
	'rating' INT,
	'price' CHAR,
	'phone' TEXT,
	'category' TEXT,
	'url' TEXT,
	'lati' DOUBLE,
	'logi' DOUBLE,
	'city' INT,
	'address' TEXT,
	'state' CHAR,
	'delivery' INT,
	'is_open' INT
	);
	'''
	cur.execute(statement)
	statement = '''
	CREATE TABLE 'city_info' (
	'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
	'name' CHAR,
	'state' CHAR,
	'county' CHAR,
	'area code' CHAR
	);
	'''
	cur.execute(statement)
	conn.commit()
	conn.close()


def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)


def make_request_using_cache(baseurl, headers, params):
    unique_ident = params_unique_combination(baseurl,params)

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.request('GET', baseurl, headers=headers, params=params)
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]


def insert_table_from_api(dict_result,category=None):
	conn = sqlite3.connect('final507.sqlite')
	cur = conn.cursor()
	res_list=dict_result['businesses']
	for res in res_list:
		try:
			m=0
			is_open=0
			if 'delivery' in res['transactions']:
				m=1
			print(res['is_closed'])
			#print(type(res['is_closed']))
			if res['is_closed']== False:
				is_open=1
			statement = '''
			INSERT INTO 'restaurants_info'
			SELECT ?,?,?,?,?,?,?,?,?, city_info.Id,?,?,?,?
			FROM city_info
			WHERE city_info.name=?
			'''
			if category!=None:
				insertion = (res['id'],res['name'],res['rating'],res['price'],res['phone'],category,res['url'],res['coordinates']['latitude'],res['coordinates']['longitude'],res['location']['address1'],res['location']['state'],m,is_open,city_name)
			else:
				insertion = (res['id'],res['name'],res['rating'],res['price'],res['phone'],res['categories'][0]['alias'],res['url'],res['coordinates']['latitude'],res['coordinates']['longitude'],res['location']['address1'],res['location']['state'],m,is_open,city_name)
			cur.execute(statement, insertion)
		except:
			continue
	conn.commit()
	conn.close()


def insert_table_from_scrap(city_name):
	baseurl = 'https://en.wikipedia.org/wiki/'+city_name
	page_text = requests.get(baseurl).text
	page_soup = BeautifulSoup(page_text, 'html.parser')
	content = page_soup.find_all(class_='mergedrow')
	result=[]
	for c in content:
		result.append(c.text.strip())
	conn = sqlite3.connect('final507.sqlite')
	cur = conn.cursor()
	state=""
	county=""
	area_code=""
	for res in result:
		res_list=res.split('\n')
		if res_list[0].lower()=="state":
			state=res_list[1]
		elif res_list[0].lower()=="county":
			county=res_list[1]
		elif res_list[0].lower()=="area code":
			area_code=res_list[1]
	try:
		insertion=(None, city_name, state, county, area_code)
		statement = 'INSERT INTO "city_info" '
		statement += 'VALUES (?,?,?,?,?)'
		cur.execute(statement, insertion)
	except:
		print("all ready saved in database!")
	conn.commit()
	conn.close()


def plot_prepare(result):
	lat_vals = []
	lon_vals = []
	text_vals = []
	for res in result:
		lat_vals.append(res[0])
		lon_vals.append(res[1])
		text_vals.append(res[2])

	data = [ dict(
		type = 'scattergeo',
		locationmode = 'USA-states',
		lon = lon_vals,
		lat = lat_vals,
		text = text_vals,
		mode = 'markers',
		marker = dict(
			size = 8,
			symbol = 'star',
			))]

	min_lat = lat_vals[0]
	max_lat = lat_vals[0]
	min_lon = lon_vals[0]
	max_lon = lon_vals[0]

	for str_v in lat_vals:
		v = float(str_v)
		if v < min_lat:
			min_lat = v
		if v > max_lat:
			max_lat = v
	for str_v in lon_vals:
		v = float(str_v)
		if v < min_lon:
			min_lon = v
		if v > max_lon:
			max_lon = v

	center_lat = (max_lat+min_lat) / 2
	center_lon = (max_lon+min_lon) / 2
	max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
	padding = max_range * .10
	lat_axis = [min_lat - padding, max_lat + padding]
	lon_axis = [min_lon - padding, max_lon + padding]

	layout = dict(
		geo = dict(
			scope='usa',
            projection=dict( type='albers usa' ),
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(100, 217, 217)",
            countrycolor = "rgb(217, 100, 217)",
            lataxis = {'range': lat_axis},
            lonaxis = {'range': lon_axis},
            center= {'lat': center_lat, 'lon': center_lon },
            countrywidth = 3,
            subunitwidth = 3
            ),
		)
	return data, layout


