import bs4
import urllib2
import ssl
import urlparse
import cookielib


class HanParse:
    def __init__(self, username, password, urlstring):
        self.setup(username, password, urlstring)

        self.token = None
        self.meter_id = None

    def setup(self, username, password, urlstring):
        # create opener from all parameters
        self.urlstring = urlstring

        url_parsed = urlparse.urlparse(urlstring)
        url_base = url_parsed.scheme + "://" + url_parsed.netloc

        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password( None, url_base, username, password )

        cj = cookielib.CookieJar()
        ssl_ctx = ssl._create_unverified_context()
        
        handlers = [ urllib2.HTTPSHandler(context=ssl_ctx),
                     urllib2.HTTPDigestAuthHandler(password_manager),
                     urllib2.HTTPCookieProcessor(cj)  ]
        self.opener = urllib2.build_opener( *handlers )

    def get_token(self):
        # set self.token
        request = urllib2.Request(self.urlstring)
        response = self.opener.open(request)
        if (response.getcode() != 200):
            return False

        soup = bs4.BeautifulSoup(response.read(), 'html.parser')
        tags = soup.find_all('input')
        self.token = tags[0].get('value')
        return True

    def get_meter_id(self):
        post_data = "tkn=" + self.token + "&action=meterform"
        request = urllib2.Request(self.urlstring, data=post_data)
        response = self.opener.open(request)
        if (response.getcode() != 200):
            return False

        soup = bs4.BeautifulSoup(response.read(), 'html.parser')
        sel = soup.find(id='meterform_select_meter')
        meter_val = sel.findChild()
        self.meter_id = meter_val.attrs.get('value')
        return True

    def get_profile(self):
        post_data = "tkn=" + self.token + "&action=showMeterProfile&mid=" + self.meter_id
        request = urllib2.Request(self.urlstring, data=post_data)
        response = self.opener.open(request)
        if (response.getcode() != 200):
            return None

        soup = bs4.BeautifulSoup(response.read(), 'html.parser')
        table_data = soup.find('table', id="metervalue")
        result_data = {
            'value': float(table_data.find(id="table_metervalues_col_wert").string),
            'unit': table_data.find(id="table_metervalues_col_einheit").string,
            'timestamp': table_data.find(id="table_metervalues_col_timestamp").string,
            'isvalid': table_data.find(id="table_metervalues_col_istvalide").string,
            'name': table_data.find(id="table_metervalues_col_name").string,
            'obis': table_data.find(id="table_metervalues_col_obis").string
        }
        return result_data
