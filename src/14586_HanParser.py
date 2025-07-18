# coding: iso-8859-15

import HTMLParser # needed for bs4
import bs4
import datetime
import urllib2
import ssl
import urlparse
import cookielib



##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class HanParser14586(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "rd_han")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_URL=1
        self.PIN_I_USERNAME=2
        self.PIN_I_PASSWORD=3
        self.PIN_O_KWH=1
        self.PIN_O_KW=2

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    def on_init(self):
        self.LOGGER.set_level(10)
        self.LOGGER.info("on_init %s" % datetime.datetime.now())

        self.prev_measurement = None
        self.prev_time = None
        self.timer = None

        self.token = None
        self.meter_id = None

        self.trigger()

    def trigger(self):
        self.username = self._get_input_value(self.PIN_I_USERNAME)
        self.password = self._get_input_value(self.PIN_I_PASSWORD)
        self.url = self._get_input_value(self.PIN_I_URL)

        if self.timer:
            self.timer.stop()
            self.timer = None
            
        if self.username and self.password and self.url:

            try:
                self.parse_measurement()
            except Exception as e:
                self.LOGGER.info("Error: %s" % e)

            self.timer = self.FRAMEWORK.create_interval()
            self.timer.set_interval(1000*900, self.on_timer_timeout)
            self.timer.start()

    def on_input_value(self, index, value):
        self.LOGGER.info("on_input_value %d %s" % (index, value))
        self.trigger()

    def parse_measurement(self):
        self.LOGGER.info("parse_measurement")
        self.setup_connection(self.username, self.password, self.url)

        
        self.get_token()
        self.LOGGER.info("Token: %s" % self.token)

        self.get_meter_id()
        self.LOGGER.info("Meter: %s" % self.meter_id)

        result_data = self.get_profile()
        measurement = float(result_data['value'])
        time = datetime.datetime.strptime(result_data['timestamp'], "%Y-%m-%d %H:%M:%S")

        self.LOGGER.info("Measurement: %f %s at %s" % (
            measurement, result_data['unit'], time))
        self._set_output_value(self.PIN_O_KWH, measurement)

        if self.prev_time and self.prev_time == time:
            # do not set any output as we queried too often
            return

        if self.prev_time:
            dt = time - self.prev_time
            kwh = measurement - self.prev_measurement
            kw = kwh / dt.total_seconds() * 3600
            self._set_output_value(self.PIN_O_KW, kw)

        self.prev_measurement = measurement
        self.prev_time = time

    def on_timer_timeout(self):
        try:
            self.parse_measurement()
        except Exception as e:
            self.LOGGER.info("Error: %s" % e)

        
    def setup_connection(self, username, password, urlstring):
        # create opener from all parameters
        self.urlstring = urlstring

        url_parsed = urlparse.urlparse(urlstring)
        url_base = url_parsed.scheme + "://" + url_parsed.netloc

        self.password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self.password_manager.add_password( None, url_base, username, password )

        self.cj = cookielib.CookieJar()
        self.ssl_ctx = ssl._create_unverified_context()
        
        handlers = [ urllib2.HTTPSHandler(context=self.ssl_ctx),
                     urllib2.HTTPDigestAuthHandler(self.password_manager),
                     urllib2.HTTPCookieProcessor(self.cj)  ]
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
