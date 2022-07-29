import json
import requests
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from PIL import Image
from io import BytesIO
from pprint import pprint
from collections import OrderedDict

from fpdf import FPDF
from fpdf.enums import XPos, YPos

class JSONData():
    def __init__(self, json_path, debug=False):
        self.debug = debug
        self.data = json.load(open(json_path, 'r'), object_hook=OrderedDict)

        # page-1 data
        self.climate_summary = self.data['climate_summary']
        self.mapping_results_summary = self.data['mapping_results_summary']
        self.currency = self.data['currency']
        self.mapping_results_image = self.data['mapping_results_image']
        self.extract_humidity_data()
        self.extract_temperature_data()

        # page-2 data
        self.location = self.data['location']
        self.crop_type = self.capitalize(self.data['crop_type'])
        self.farm_size = self.data['farm_size']
        self.tech_profile = self.data['tech_profile']
        self.growth_method = self.data['growth_method']
        self.structure = self.data['structure']
        self.yearly_growth_cycles = self.data['yearly_growth_cycles']
        self.extract_recommended_roi_data()
        self.extract_alternatives_data()
        self.extract_greenhouse_data()
        self.extract_capex_data()
        self.extract_opex_data()
        self.extract_roi_data()

        # page-3 data
        self.extract_variable_expenses_data()
        self.extract_fixed_expenses_data()
        self.extract_p_and_l_data()
        self.extract_sensitivity_data()
    
    @staticmethod
    def capitalize(string):
        return ' '.join([substr.capitalize() for substr in string.split('_')])
    
    def extract_humidity_data(self, debug=False):
        # extract humidity data
        self.months_humidity = list(self.data['humidity_data'].keys())
        self.humidity_data = [[], []]
        for m in self.months_humidity:
            self.humidity_data[0].append(self.data['humidity_data'][m]['average_daily_max'])
            self.humidity_data[1].append(self.data['humidity_data'][m]['average_daily_min'])
        self.months_humidity = ['Months'] + self.months_humidity[::-1]
        self.months_humidity = list(map(lambda x: x.capitalize(), self.months_humidity))
        self.humidity_data[0] = ['Average daily - maximum'] + self.humidity_data[0][::-1]
        self.humidity_data[1] = ['Average daily - minimum'] + self.humidity_data[1][::-1]
        if debug: print('[self.months_humidity]', self.months_humidity)
        if debug: print('[humidity_data]', self.humidity_data[0])
        if debug: print('[humidity_data]', self.humidity_data[1])

    def extract_temperature_data(self, debug=False):
        # extract temperature data
        self.months_temperature = list(self.data['temperature_data'].keys())
        self.temperature_data = [[], [], []]
        for m in self.months_temperature:
            max_val = self.data['temperature_data'][m]['average_daily_max']
            min_val = self.data['temperature_data'][m]['average_daily_min']
            self.temperature_data[0].append(max_val)
            self.temperature_data[1].append(min_val)
            self.temperature_data[2].append(max_val - min_val)
        self.months_temperature = ['Months'] + self.months_temperature[::-1]
        self.months_temperature = list(map(lambda x: x.capitalize(), self.months_temperature))
        self.temperature_data[0] = ['Average daily - maximum'] + self.temperature_data[0][::-1]
        self.temperature_data[1] = ['Average daily - minimum'] + self.temperature_data[1][::-1]
        self.temperature_data[2] = ['Average daily - fluctuation'] + self.temperature_data[2][::-1]
        if debug: print('[months_temperature]', self.months_temperature)
        if debug: print('[temperature_data]', self.temperature_data[0])
        if debug: print('[temperature_data]', self.temperature_data[1])
        if debug: print('[temperature_data]', self.temperature_data[2])

    def extract_recommended_roi_data(self, debug=False):
        # extract recommended_roi data
        self.recommended_roi = OrderedDict()
        for key, value in self.data['recommended_roi'].items():
            self.recommended_roi[self.capitalize(key)] = value

        if debug: print('[recommended_roi]')
        if debug: pprint(self.recommended_roi)

    def extract_alternatives_data(self, debug=False):
        # extract alternatives data
        self.alternative_data = OrderedDict()
        for key, value_list in self.data['alternative_by_tech'].items():
            key = self.capitalize(key)
            self.alternative_data[key] = OrderedDict({'size': [], 'capex': []})
            for obj in value_list:
                self.alternative_data[key]['size'].append(obj['size'])
                self.alternative_data[key]['capex'].append(obj['capex'])

        if debug: print('[alternative_data]')
        if debug: pprint(self.alternative_data)

    def extract_greenhouse_data(self, debug=False):
        # extract greenhouse_images data
        self.greenhouse_data = self.data['greenhouse_images']
        if debug: print('[greenhouse_data]')
        if debug: pprint(self.greenhouse_data)

    def extract_capex_data(self, debug=False):
        # extract capex data
        self.capex_data = {
            'growth_method': self.data['capex']['growth_method'], 
            'total_capex': self.data['capex']['total_capex'], 
            'data': [], 
        }
        for row in self.data['capex']['capex_breakdown']:
            self.capex_data['data'].append([row['name'], row['cost']])
        if debug: print('[capex_data]')
        if debug: pprint(self.capex_data)

    def extract_opex_data(self, debug=False):
        # extract opex data
        self.opex_data = {
            'header': ['Inputs', 'Annual Total'], 
            'body': [], 
            'footer': ['Total', self.data['opex']['total']], 
        }
        for row in self.data['opex']['breakdown']:
            self.opex_data['body'].append([row['name'], row['cost']])
        if debug: print('[opex_data]')
        if debug: pprint(self.opex_data)

    def extract_roi_data(self, debug=False):
        # extract roi data
        self.roi_data = {
            'percentage': self.data['roi']['percentage'], 
            'years': self.data['roi']['years'], 
            'roi_trend': OrderedDict({'years': [], 'roi': []}), 
        }
        for obj in self.data['roi']['roi_trend']:
            self.roi_data['roi_trend']['years'].append(obj['years'])
            self.roi_data['roi_trend']['roi'].append(obj['roi'])

        if debug: print('[roi_data]')
        if debug: pprint(self.roi_data)

    def extract_variable_expenses_data(self, debug=False):
        # extract variable_expenses data
        self.variable_expenses_data = self.opex_data

    def extract_fixed_expenses_data(self, debug=False):
        # extract fixed_expenses data
        self.fixed_expenses_data = {
            'header': ['Inputs', 'Annual Total'], 
            'body': [], 
            'footer': ['Total', self.data['fixed_expenses']['total']], 
        }
        for row in self.data['fixed_expenses']['breakdown']:
            self.fixed_expenses_data['body'].append([row['name'], row['cost']])
        if debug: print('[fixed_expenses_data]')
        if debug: pprint(self.fixed_expenses_data)

    def extract_p_and_l_data(self, debug=False):
        # extract p_and_l data
        self.p_and_l_data = {'body': []}
        for row in self.data['p_and_l']:
            self.p_and_l_data['body'].append([row['name'], row['cost']])
        if debug: print('[p_and_l_data]')
        if debug: pprint(self.p_and_l_data)

    def extract_sensitivity_data(self, debug=False):
        # extract sensitivity data
        sensitivity_breakdown = self.data['sensitivity']['breakdown']
        self.sensitivity_data = [[*[obj['market_price'] for obj in sensitivity_breakdown[0]['net_income']], 'production_units', 'production_calculation']]
        for obj1 in sensitivity_breakdown:
            row = []
            for obj2 in obj1['net_income']:
                row.append(obj2['income'])
            row += [obj1['production_units'], obj1['production_calculation']]
            self.sensitivity_data.append(row)
        if debug: print('[sensitivity_data]')
        if debug: pprint(self.sensitivity_data)

class PDF(FPDF):

    WIDTH, HEIGHT = 0, 0

    def create_background(self, x, y, w, h, color):
        self.set_fill_color(*color)
        self.set_xy(x, y)
        self.cell(w, h, '', fill=1)

    def create_page_title(self, title, color, y, h=10):
        # add page title
        self.set_font_size(16)
        page_title_width = self.get_string_width(title)
        self.set_text_color(*color)
        self.set_xy((self.WIDTH - page_title_width) / 2, y)
        self.cell(page_title_width, h, title, align='C')

    def to_currency(self, num, symbol=True, decimal=False):
        if symbol and decimal:
            currency = f'{data.currency} {num:,.2f}'
        elif symbol:
            currency = f'{data.currency} {num:,}'
        else:
            currency = f'{num:,}'
        return currency

    def create_section(self, title, data, x, y, w, h, image_path=None):
        self.create_background(x, y, w, h, (255, 255, 255))
        # add section title
        self.set_text_color(0)
        self.set_font(style='B', size=12)
        self.set_xy(x + 6, y + 4)
        self.cell(w, 10, title, align='L')

        if image_path:
            # add section text
            self.set_text_color(180)
            self.set_font(style='', size=11)
            self.set_xy(x + 6, y + 14)
            self.multi_cell(w * 0.4, h=None, txt=data, align='L')
            # response = requests.get(image_path)
            response = requests.get('https://pic.onlinewebfonts.com/svg/img_148071.png')
            img = Image.open(BytesIO(response.content))
            self.image(img, x + w * 0.4 + 10, y + 2, h=h - 4)
        else:
            # add section text
            self.set_text_color(180)
            self.set_font(style='', size=11)
            self.set_xy(x + 6, y + 17)
            self.cell(w, 0, data, align='L')

    def create_simple_table(self, headings, data, title, dims, paddings):
        x, y, w, h = dims
        pad_T, pad_R, pad_B, pad_L = paddings
        # add section background
        self.set_fill_color(255)
        self.set_text_color(0)
        self.set_xy(x, y)
        self.cell(w, h, '', fill=1)

        # add table title
        self.set_font(style='B', size=14)
        self.set_xy(x + pad_L, y + pad_T)
        self.cell(0, 10, title, new_x=XPos.LEFT, new_y=YPos.NEXT)

        # Colors, line width and bold font:
        self.set_fill_color(155, 204, 181)
        self.set_text_color(100)
        self.set_draw_color(150, 210, 180)
        self.set_line_width(0.1)
        self.set_font(style='', size=9)
        col_widths = [50] + [(w - 50 - pad_R - pad_L) / 12] * 12

        # add header rows
        self.set_xy(x + pad_L, y + pad_T + 10)
        for i, (col_width, heading) in enumerate(zip(col_widths, headings)):
            self.cell(col_width, 8, heading, border=1, align='L' if i == 0 else 'C', fill=True)

        # add data rows
        self.set_xy(x + pad_L, y + pad_T + 18)
        for j, row in enumerate(data):
            for i in range(len(row)):
                if i == 0:
                    self.set_text_color(155, 204, 181)
                    self.set_fill_color(240)
                else:
                    self.set_text_color(180)
                    self.set_fill_color(255)
                self.cell(col_widths[i], 8, str(row[i]), border=1, align='L' if i == 0 else 'C', fill=True)
            self.set_xy(x + pad_L, y + pad_T + 18 + (j + 1) * 8)
        self.cell(sum(col_widths), 0, '', 'T')

    def create_finance_report_table(self, data, title, dims, paddings, col_widths, row_height):
        x, y, w, h = dims
        pad_T, pad_R, pad_B, pad_L = paddings

        # add section background
        self.create_background(x, y, w, h, (255, 255, 255))

        # add table title
        self.set_text_color(0)
        self.set_font(style='B', size=11)
        x2, y2 = x + pad_L, y + pad_T
        self.set_xy(x2, y2)
        self.cell(0, 10, title)

        # Colors, line width and bold font:
        self.set_line_width(0.1)
        self.set_draw_color(150, 210, 180)
        self.set_font(style='', size=9)
        self.set_fill_color(155, 204, 181)
        self.set_text_color(100)
        
        # add header rows
        if 'header' in data:
            y2 = y2 + 12
            self.set_xy(x2, y2)
            for i, (col_width, value) in enumerate(zip(col_widths, data['header'])):
                self.cell(col_width, row_height, str(value), border=1, align='L' if i == 0 else 'C', fill=True)
        else:
            y2 = y2 + 12 - row_height

        # add data rows
        y2 = y2 + row_height
        self.set_xy(x2, y2)
        self.set_text_color(180)
        for j, row in enumerate(data['body']):
            for i in range(len(row)):
                self.set_fill_color(240 if i == 0 else 255)
                value = row[i] if type(row[i]) is str else self.to_currency(row[i])
                self.cell(col_widths[i], row_height, value, border=1, align='L' if i == 0 else 'C', fill=True)
            y2 = y2 + row_height
            self.set_xy(x2, y2)

        if 'footer' in data:
            self.set_draw_color(150, 210, 180)
            self.set_line_width(0.1)
            self.set_xy(x2, y2)
            for i, (col_width, value) in enumerate(zip(col_widths, data['footer'])):
                self.set_fill_color(240 if i == 0 else 255)
                value = value if type(value) is str else self.to_currency(value)
                self.cell(col_width, row_height, value, border=1, align='L' if i == 0 else 'C', fill=True)
            self.set_line_width(0.5)
            self.set_draw_color(0, 128, 0)
            self.line(x1=x2, y1=y2, x2=x2+sum(col_widths), y2=y2)

    def create_sensitivity_table(self, data, title, dims, paddings, col_width, row_height):
        x, y, w, h = dims
        pad_T, pad_R, pad_B, pad_L = paddings

        # add section background
        self.create_background(x, y, w, h, (255, 255, 255))

        # add table title
        self.set_text_color(0)
        self.set_font(style='B', size=11)
        x2, y2 = x + pad_L, y + pad_T
        self.set_xy(x2, y2)
        self.cell(0, 10, title)

        # Colors, line width and bold font:
        self.set_line_width(0.1)
        self.set_draw_color(150, 210, 180)
        self.set_font(style='', size=9)
        self.set_text_color(100)

        # add top most row
        y2 = y2 + 12
        self.set_fill_color(155, 204, 181)
        self.set_xy(x2 + col_width, y2)
        self.cell(col_width * 4, row_height, 'Market Price', border=1, align='C', fill=True)
        # add left most column
        self.set_fill_color(240)
        self.set_xy(x2, y2 + row_height)
        self.cell(col_width, row_height * 5, 'Net Income', border=1, align='C', fill=True)

        # add data rows
        x2 = x2 + col_width
        y2 = y2 + row_height
        self.set_xy(x2, y2)
        self.set_text_color(180)
        for j, row in enumerate(data):
            for i in range(len(row)):
                value = row[i]
                if j == 0 and i in [len(row) - 2, len(row) - 1]:
                    self.set_fill_color(240)
                else:
                    self.set_fill_color(255)
                
                if j == 0:
                    value = JSONData.capitalize(value) if type(value) is str else self.to_currency(value, True, True)
                elif i == len(row) - 2:
                    value = self.to_currency(value, False, False)
                elif i == len(row) - 1:
                    value = f'{value} %'
                else:
                    value = self.to_currency(value)
                self.cell(col_width if i != len(row) - 1 else col_width + 12, row_height, value, border=1, align='C', fill=True)
            y2 = y2 + row_height
            self.set_xy(x2, y2)
        self.cell(col_width * 6 + 12, 0, '', 'T')

    def create_page2_info(self, title, value, x, y, w, h, color, image_path):
        self.create_background(x, y, w, h, color)
        self.image(image_path, x + 2, y + 2, h - 4, h - 4)
        # add info title
        self.set_text_color(0)
        self.set_font(style='B', size=12)
        self.set_xy(x + h, y + 2)
        self.cell(w, 10, title, align='L')
        # add info value
        self.set_text_color(180)
        self.set_font(size=10)
        self.set_xy(x + h, y + 8)
        self.cell(w, 10, value, align='L')

    def create_page2_recommended_roi(self, data_recommended_roi, x, y, w, h, color):
        self.create_background(x, y, w, h, color)
        self.set_font('helvetica', size=10)
        self.set_draw_color(230)
        self.set_xy(x + 4, y)
        text = 'Best ROI (Recommended)'
        self.cell(self.get_string_width(text), 10, text)
        roi_keys = list(data_recommended_roi.keys())
        roi_values = list(data_recommended_roi.values())
        # line 1
        self.set_xy(x + 4, y + 20)
        self.set_text_color(180)
        self.cell(28, 12, roi_keys[0], border='TB')
        self.set_text_color(83, 173, 106)
        self.cell(18, 12, f'{roi_values[0]} months', border='TB', align='R')
        # line 2
        self.set_xy(x + 4, y + 32)
        self.set_text_color(180)
        self.cell(28, 12, roi_keys[1], border='TB')
        self.set_text_color(83, 173, 106)
        self.cell(18, 12, f'{roi_values[1]} Years', border='TB', align='R')
        # line 3
        self.set_xy(x + 4, y + 44)
        self.set_text_color(180)
        self.cell(28, 12, roi_keys[2], border='TB')
        self.set_text_color(83, 173, 106)
        self.cell(18, 12, f'{roi_values[2]} M', border='TB', align='R')
        self.set_font_size(6)
        self.set_text_color(180)
        self.set_xy(x + 32, y + 48)
        self.cell(18, 12, '$ American Dollars', align='R')

    def create_page2_alternatives(self, data_alternatives, x, y, w, h, color):
        self.create_background(x, y, w, h, color)
        # create plot
        plt.style.use('seaborn-whitegrid')
        fig, ax = plt.subplots(figsize=(10, 4))
        x_ticks = None
        for key, value in data_alternatives.items():
            if not x_ticks: x_ticks = value['size']
            ax.plot(value['size'], value['capex'], marker='o', label=key.capitalize())
        # shrink axis height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        # remove border of plot
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        # set properties of plot and save
        ax.set_xticks(x_ticks)
        ax.grid(axis='x')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
        plt.savefig('alternatives_plot.jpg', dpi=300)
        self.image('alternatives_plot.jpg', x, y, w, h)
        # create plot title
        self.set_font('helvetica', size=10)
        self.set_draw_color(230)
        self.set_xy(x, y)
        text = 'Alternatives by Budget & Tech'
        self.cell(w, 10, text, align='C')

    def create_page2_greenhouse(self, data_greenhouse, x, y, w, h, color):
        self.create_background(x, y, w, h, color)
        # create title
        self.set_font('helvetica', size=10)
        self.set_text_color(180)
        self.set_xy(x, y)
        text = 'Gothic 9.6 Greenhouse 3D Layout'
        self.cell(w, 10, text, align='C')
        # fetch and draw images
        # response = requests.get(data_greenhouse['image_1'])
        response = requests.get('https://pic.onlinewebfonts.com/svg/img_148071.png')
        img = Image.open(BytesIO(response.content))
        img_w, img_h = (w - 8) / 2, (h - 14) / 2
        self.image(img, x + 4, y + 10, img_w, img_h)
        # response = requests.get(data_greenhouse['image_1'])
        response = requests.get('https://user-images.githubusercontent.com/2351721/31314483-7611c488-ac0e-11e7-97d1-3cfc1c79610e.png')
        img = Image.open(BytesIO(response.content))
        self.image(img, x + 4 + img_w, y + 10, img_w, img_h)
        # response = requests.get(data_greenhouse['image_1'])
        response = requests.get('https://cdn3.iconfinder.com/data/icons/design-n-code/100/272127c4-8d19-4bd3-bd22-2b75ce94ccb4-512.png')
        img = Image.open(BytesIO(response.content))
        self.image(img, x + 4, y + 10 + img_h, img_w, img_h)
        # response = requests.get(data_greenhouse['image_1'])
        response = requests.get('https://image.shutterstock.com/image-vector/photo-album-picture-collection-line-260nw-256926565.jpg')
        img = Image.open(BytesIO(response.content))
        self.image(img, x + 4 + img_w, y + 10 + img_h, img_w, img_h)

    def create_page2_capex(self, data_capex, x, y, w, h, color):
        self.create_background(x, y, w, h, color)
        self.set_font('helvetica', size=9)
        self.set_text_color(180)
        self.set_xy(x + 1, y)
        self.cell(20, 10, 'Capex')

        self.set_text_color(150, 210, 180)
        text = self.to_currency(data_capex['total_capex'])
        self.set_xy(x + w - self.get_string_width(text) - 2, y)
        self.cell(self.get_string_width(text), 10, text, align='R')

        self.set_font('helvetica', style='B', size=8)
        self.set_text_color(0)
        self.set_xy(x, y)
        self.cell(w, 10, 'Advance Method', align='C')
        self.set_xy(x, y + 4)
        self.cell(w, 10, 'Specification per Dunam', align='C')

        self.set_text_color(180)
        self.set_font('helvetica', size=7)
        self.set_draw_color(230)
        self.set_xy(x, y + 5)
        self.line(x + 18, y + 12, x + w - 18, y + 12)

        x2, y2 = x + 18, y + 15
        for i, row in enumerate(data_capex['data']):
            self.set_xy(x2, y2)
            text_w1 = self.get_string_width(row[0])
            text_w2 = self.get_string_width(self.to_currency(row[1]))
            self.cell(48, 4, row[0], align='L')
            self.set_xy(x2 + text_w1 + 2, y2)
            self.cell(48 - text_w1, 4, self.to_currency(row[1]), align='R')
            self.set_dash_pattern()
            self.line(x2 + text_w1 + 2, y2 + 2, x2 + 48 - text_w2, y2 + 2)
            y2 = y2 + 3.5

    def create_page2_opex(self, data_opex, x, y, w, h, color):
        self.create_background(x, y, w, h, color)
        # create plot
        names = [f'{row[0]}, {self.to_currency(row[1])}' for row in data_opex['body']]
        sizes = [row[1] for row in data_opex['body']]
        r, g, b = 55, 140, 97
        r, g, b = r/255, g/255, b/255
        plt.style.use('seaborn-whitegrid')
        fig, ax = plt.subplots(figsize=(10, 5), subplot_kw=dict(aspect='equal'))
        wedges, texts = ax.pie(sizes, wedgeprops=dict(width=0.5), startangle=-40)
        kw = {
            'arrowprops': {'arrowstyle': '-', 'linestyle': '--', 'linewidth': 1, 'color': (r, g, b)}, 
            'zorder': 10, 'va': 'center', 'color': (r, g, b)
        }
        for i, p in enumerate(wedges):
            ang = (p.theta2 + p.theta1) / 2
            py = np.sin(np.deg2rad(ang))
            px = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: 'right', 1: 'left'}[int(np.sign(px))]
            connectionstyle = 'angle,angleA=0,angleB={}'.format(ang)
            kw['arrowprops'].update({'connectionstyle': connectionstyle})
            ax.plot()
            ax.annotate(names[i], xy=(px * 0.8, py * 0.8), xytext=(1.35 * np.sign(px), 1.2 * py),
                        horizontalalignment=horizontalalignment, **kw)
        plt.tight_layout()
        plt.savefig('opex_plot.jpg', dpi=300)
        self.image('opex_plot.jpg', x + w / 10, y + 6, h=h*0.9)

        self.set_font('helvetica', size=9)
        self.set_text_color(180)
        self.set_xy(x + 1, y)
        self.cell(20, 10, 'Opex')

        self.set_text_color(150, 210, 180)
        text = self.to_currency(data.opex_data['footer'][1])
        self.set_xy(x + w - self.get_string_width(text) - 2, y)
        self.cell(self.get_string_width(text), 10, text, align='R')

        # create plot title
        self.set_font('helvetica', style='B', size=8)
        self.set_text_color(0)
        self.set_xy(x, y)
        self.cell(w, 10, 'Variable Expenses', align='C')
    
    def create_page2_roi(self, data_roi, x, y, w, h, color):
        self.create_background(x, y, w, h, color)
        # create plot
        plt.style.use('seaborn-whitegrid')
        fig, ax = plt.subplots(figsize=(10, 7))
        years = data_roi['roi_trend']['years']
        roi = data_roi['roi_trend']['roi']
        r, g, b = 55, 140, 97
        r, g, b = r/255, g/255, b/255
        rgb = (r, g, b)
        ax.fill_between(years, roi, min(roi), color=(r, g, b, 0.3))
        ax.plot(years, roi, color=rgb, marker='o', markeredgecolor=rgb, markerfacecolor='w', 
                markersize=10, markeredgewidth=2, linewidth=2, label='Years of Investment')
        ax.axhline(0, color='r')
        # shrink axis height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width, box.height * 0.8])
        # remove border of plot
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        # set properties of plot and save
        ax.set_xticks(years)
        ax.tick_params(axis='both', which='major', labelsize=18)
        ax.grid(axis='x')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25), fontsize=18)
        plt.savefig('roi_plot.jpg', dpi=300)
        self.image('roi_plot.jpg', x + w * 0.02, y, w=w*0.98)

        # create left corner text
        self.set_font('helvetica', size=9)
        self.set_text_color(180)
        self.set_xy(x + 1, y)
        self.cell(20, 10, f"{data_roi['percentage']}% ROI")
        # create right corner text
        self.set_text_color(150, 210, 180)
        text = f"{data_roi['years']} Years"
        self.set_xy(x + w - self.get_string_width(text) - 2, y)
        self.cell(self.get_string_width(text), 10, text, align='R')
        # create plot title
        self.set_font('helvetica', style='B', size=8)
        self.set_text_color(0)
        self.set_xy(x, y)
        self.cell(w, 10, 'ROI Thousands NIS', align='C')

########## first page ##########
def add_page1(pdf, data):
    pdf.add_page()
    # add logo
    pdf.image('full_logo.png', x=(pdf.WIDTH - 32) / 2, y=4, w=32)
    # add main rectangle background
    pdf.create_background(3, 29, 350, 177, (235, 235, 235))
    # add page title
    pdf.create_page_title('Climate & Mapping Results', (150, 150, 150), 32, 10)
    # add climate summary section
    pdf.create_section('Climate Summary', data.climate_summary, 16, 48, (pdf.WIDTH - 22) / 2, 47)
    # add mapping results section
    pdf.create_section('Mapping Results', data.mapping_results_summary, (pdf.WIDTH + 16) / 2, 48, (pdf.WIDTH - 48) / 2, 47, 'placeholder-2.png')
    # add humidity table section
    pdf.create_simple_table(
        headings=data.months_humidity, 
        data=data.humidity_data, 
        title='Humidity', 
        dims=[16, 98, pdf.WIDTH - 32, 45], 
        paddings=[2, 8, 4, 8]
    )
    # add temperature table section
    pdf.create_simple_table(
        headings=data.months_temperature, 
        data=data.temperature_data, 
        title='Temperature', 
        dims=[16, 146, pdf.WIDTH - 32, 55], 
        paddings=[2, 8, 4, 8]
    )

########## second page ##########
def add_page2(pdf, data):
    pdf.add_page()
    # add logo
    pdf.image('full_logo.png', x=(pdf.WIDTH - 32) / 2, y=4, w=32)
    # add main rectangle background
    pdf.create_background(3, 29, 350, 177, (235, 235, 235))
    # pdf.create_background(3, 20, 350, 177, (235, 235, 235))
    # write 'Location' text
    x_coord, y_coord = 16, 34
    pdf.set_text_color(150)
    pdf.set_font('helvetica', size=11)
    pdf.set_xy(x_coord, y_coord)
    pdf.cell(pdf.get_string_width('Location:'), 10, 'Location:')
    # draw location background with actual location
    pdf.set_text_color(50)
    pdf.set_fill_color(255)
    pdf.set_font('helvetica', style='B', size=12)
    location_width = pdf.get_string_width(data.location)
    x_coord += 24
    pdf.set_xy(x_coord, y_coord)
    pdf.cell(location_width + 18, 10, '', fill=True)
    pdf.image('location-icon.png', x=42, y=35, h=8)
    x_coord += 8
    pdf.set_xy(x_coord, y_coord)
    pdf.cell(location_width, 10, data.location)
    # write 'Crop Type' text
    pdf.set_text_color(150)
    pdf.set_font('helvetica', size=11)
    x_coord += location_width + 15
    pdf.set_xy(x_coord, y_coord)
    pdf.cell(pdf.get_string_width('Crop Type:'), 10, 'Crop Type:')
    # draw crop_type background with actual crop_type
    pdf.set_text_color(50)
    pdf.set_font('helvetica', style='B', size=12)
    crop_type_width = pdf.get_string_width(data.crop_type)
    x_coord += 32
    pdf.set_xy(x_coord - 5, y_coord)
    pdf.cell(crop_type_width + 10, 10, '', fill=True)
    pdf.set_xy(x_coord, y_coord)
    pdf.cell(crop_type_width, 10, data.crop_type, align='C')
    # create page 2 info sections
    x_coord, y_coord = 16, 47
    pdf.create_page2_info(f'{data.farm_size} Dunum', 'Farm Size', x_coord, y_coord, 62, 20, (255, 255, 255), 'placeholder-2.png')
    x_coord += 66
    pdf.create_page2_info(data.tech_profile, 'Tech Profile', x_coord, y_coord, 62, 20, (255, 255, 255), 'placeholder-2.png')
    x_coord += 66
    pdf.create_page2_info(data.growth_method, 'Growth Method', x_coord, y_coord, 62, 20, (255, 255, 255), 'placeholder-2.png')
    x_coord += 66
    pdf.create_page2_info(data.structure, 'Structure', x_coord, y_coord, 62, 20, (255, 255, 255), 'placeholder-2.png')
    x_coord += 66
    pdf.create_page2_info(str(data.yearly_growth_cycles), 'Growth Cycles', x_coord, y_coord, 62, 20, (255, 255, 255), 'placeholder-2.png')
    # create_page2_recommended_roi
    pdf.create_page2_recommended_roi(data.recommended_roi, 16, 72, 55, 63, (255, 255, 255))
    # create_page2_alternatives
    pdf.create_page2_alternatives(data.alternative_data, 75, 72, 174, 63, (255, 255, 255))
    # # create_page2_greenhouse
    pdf.create_page2_greenhouse(data.greenhouse_data, 254, 72, 88, 63, (255, 255, 255))
    # create_page2_capex
    pdf.create_page2_capex(data.capex_data, 16, 139, 86, 63, (255, 255, 255))
    # create_page2_opex
    pdf.create_page2_opex(data.opex_data, 108, 139, 141, 63, (255, 255, 255))
    # create_page2_roi
    pdf.create_page2_roi(data.roi_data, 254, 139, 88, 63, (255, 255, 255))

########## third page ##########
def add_page3(pdf, data):
    pdf.add_page()
    # add logo
    pdf.image('full_logo.png', x=(pdf.WIDTH - 32) / 2, y=4, w=32)
    # add main rectangle background
    pdf.create_background(3, 29, 350, 177, (235, 235, 235))
    # pdf.create_background(3, 20, 350, 177, (235, 235, 235))
    pdf.create_page_title(title='Finance Report', color=(150, 150, 150), y=33)
    # add variable expanse table
    pdf.create_finance_report_table(
        data=data.variable_expenses_data,
        title='Variable Expenses',
        dims=(17, 47, 105, 155),
        paddings=(3, 8, 5, 8),
        col_widths=(44, 44),
        row_height=12,
    )
    # add fixed expanse table
    pdf.create_finance_report_table(
        data=data.fixed_expenses_data,
        title='Fixed Expenses',
        dims=(128, 47, 103, 78),
        paddings=(3, 10, 5, 10),
        col_widths=(41, 41),
        row_height=8,
    )
    # add P&L table
    pdf.create_finance_report_table(
        data=data.p_and_l_data,
        title='P&L',
        dims=(236, 47, 103, 78),
        paddings=(3, 10, 5, 10),
        col_widths=(41, 41),
        row_height=8,
    )
    # add sensitivity table
    pdf.create_sensitivity_table(
        data=data.sensitivity_data,
        title='Sensitivity Table',
        dims=(128, 129, 211, 73),
        paddings=(3, 6, 5, 6),
        col_width=27,
        row_height=8,
    )

##############################

json_path = 'report_data_structure2.json'
data = JSONData(json_path)
# legal (W x H) -> 216mm x 356mm
pdf = PDF('L', 'mm', 'legal')
pdf.WIDTH, pdf.HEIGHT = 356, 216
pdf.set_font('helvetica', size=9)
pdf.set_margin(0)
add_page1(pdf, data)
add_page2(pdf, data)
add_page3(pdf, data)

# save pdf file
pdf.output('generated.pdf')
