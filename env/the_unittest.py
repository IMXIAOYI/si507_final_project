import model
import unittest
import secret
import sqlite3
import requests
from bs4 import BeautifulSoup

class Test_data_access(unittest.TestCase):
    def test_update_city_name(self):
    	new_city_name='Chicago'
    	model.init(new_city_name)
    	self.assertEqual(model.city_name,new_city_name)

    def test_access_api_through_category(self):
        category='bars'
        baseurl='https://api.yelp.com/v3/businesses/search'
        headers={'Authorization': 'Bearer %s' % secret.api_key}
        params={}
        params['location']='Chicago'
        params['categories']=category
        results=model.make_request_using_cache(baseurl,headers,params)
        self.assertEqual(results['businesses'][0]['location']['city'],'Chicago')
    
    def test_access_api_through_open_now(self):
        baseurl='https://api.yelp.com/v3/businesses/search'
        headers={'Authorization': 'Bearer %s' % secret.api_key}
        params={}
        params['location']='Chicago'
        params['open_now']=True
        results=model.make_request_using_cache(baseurl,headers,params)
        self.assertEqual(results['businesses'][0]['location']['city'],'Chicago')
        self.assertEqual(results['businesses'][0]['is_closed'],False)

    def test_access_api_through_price_range(self):
        baseurl='https://api.yelp.com/v3/businesses/search'
        headers={'Authorization': 'Bearer %s' % secret.api_key}
        params={}
        params['location']='Chicago'
        params['price']=2
        results=model.make_request_using_cache(baseurl,headers,params)
        self.assertEqual(results['businesses'][0]['location']['city'],'Chicago')
        self.assertEqual(results['businesses'][0]['price'],'$$')

    def test_access_web_scrap(self):
        baseurl = 'https://en.wikipedia.org/wiki/'+'Ann Arbor'
        page_text = requests.get(baseurl).text
        page_soup = BeautifulSoup(page_text, 'html.parser')
        content = page_soup.find_all(class_='mergedrow')
        result=[]
        for c in content:
            result.append(c.text.strip())
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
        self.assertEqual(state,'Michigan')
        self.assertEqual(county,'Washtenaw')
        self.assertEqual(area_code,'734')


class Test_storage(unittest.TestCase):
    def test_insert_table_from_category(self):
        model.init('Chicago')
        model.insert_table_from_scrap('Chicago')
        category='bars'
        baseurl='https://api.yelp.com/v3/businesses/search'
        headers={'Authorization': 'Bearer %s' % secret.api_key}
        params={}
        params['location']='Chicago'
        params['categories']=category
        results=model.make_request_using_cache(baseurl,headers,params)
        model.insert_table_from_api(results,'bars')
        conn = sqlite3.connect('final507.sqlite')
        cur = conn.cursor()
        statement='select * from restaurants_info where id=?'
        cur.execute(statement,[results['businesses'][0]['id']])
        result=cur.fetchone()
        self.assertEqual(results['businesses'][0]['id'],result[0])
        conn.commit()
        conn.close()
        

    def test_insert_table_from_open_now(self):
        model.init('Chicago')
        model.insert_table_from_scrap('Chicago')
        baseurl='https://api.yelp.com/v3/businesses/search'
        headers={'Authorization': 'Bearer %s' % secret.api_key}
        params={}
        params['location']='Chicago'
        params['open_now']=True
        results=model.make_request_using_cache(baseurl,headers,params)
        model.insert_table_from_api(results,'bars')
        conn = sqlite3.connect('final507.sqlite')
        cur = conn.cursor()
        statement='select * from restaurants_info where id=?'
        cur.execute(statement,[results['businesses'][0]['id']])
        result=cur.fetchone()
        self.assertEqual(results['businesses'][0]['id'],result[0])
        conn.commit()
        conn.close()

    def test_insert_table_from_price_range(self):
        model.init('Chicago')
        model.insert_table_from_scrap('Chicago')
        baseurl='https://api.yelp.com/v3/businesses/search'
        headers={'Authorization': 'Bearer %s' % secret.api_key}
        params={}
        params['location']='Chicago'
        params['price']=2
        results=model.make_request_using_cache(baseurl,headers,params)
        model.insert_table_from_api(results,'bars')
        conn = sqlite3.connect('final507.sqlite')
        cur = conn.cursor()
        statement='select * from restaurants_info where id=?'
        cur.execute(statement,[results['businesses'][0]['id']])
        result=cur.fetchone()
        self.assertEqual(results['businesses'][0]['id'],result[0])
        conn.commit()
        conn.close()

    def test_insert_table_from_web_scrap(self):
        model.insert_table_from_scrap('Ann Arbor')
        conn = sqlite3.connect('final507.sqlite')
        cur = conn.cursor()
        statement='select * from city_info where name="Ann Arbor"'
        cur.execute(statement)
        result=cur.fetchone()
        self.assertEqual('Ann Arbor',result[1])

class Test_processing(unittest.TestCase):
    def test_plot_prepare_type(self):
        model.init('Chicago')
        model.insert_table_from_scrap('Chicago')
        baseurl='https://api.yelp.com/v3/businesses/search'
        headers={'Authorization': 'Bearer %s' % secret.api_key}
        params={}
        params['location']='Chicago'
        params['price']=2
        results=model.make_request_using_cache(baseurl,headers,params)
        model.insert_table_from_api(results,'bars')
        conn = sqlite3.connect('final507.sqlite')
        cur = conn.cursor()
        statement='select r.lati,r.logi,r.name,r.id from restaurants_info as r join city_info as c on c.Id=r.city where r.price=? and c.name =? limit 20'
        cur.execute(statement,('$$', 'Chicago'))
        result=cur.fetchall()
        data,style=model.plot_prepare(result)
        self.assertIsInstance(data,list)
        self.assertIsInstance(style,dict)

    def params_conbime(self):
        result=model.params_unique_combination('www.fake.com',{'name':'yi','gender':'female'})
        self.assertEqual(result,'www.fake.comname-yi_gender-female')

if __name__ == '__main__':
    unittest.main()
