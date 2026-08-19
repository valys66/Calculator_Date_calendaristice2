from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp
from kivy.core.clipboard import Clipboard
from datetime import datetime, date, timedelta
import calendar
from dateutil.relativedelta import relativedelta

# Zilele săptămânii în română
ZILE_RO = {
    "Monday": "Luni",
    "Tuesday": "Marți",
    "Wednesday": "Miercuri",
    "Thursday": "Joi",
    "Friday": "Vineri",
    "Saturday": "Sâmbătă",
    "Sunday": "Duminică"
}

LUNI_RO_LIST = [
    "Ianuarie", "Februarie", "Martie", "Aprilie",
    "Mai", "Iunie", "Iulie", "August",
    "Septembrie", "Octombrie", "Noiembrie", "Decembrie"
]

LUNI_RO_DICT = {luna: i+1 for i, luna in enumerate(LUNI_RO_LIST)}

def determina_zodie(zi, luna):
    if (luna == 3 and zi >= 21) or (luna == 4 and zi <= 19): return "Berbec"
    elif (luna == 4 and zi >= 20) or (luna == 5 and zi <= 20): return "Taur"
    elif (luna == 5 and zi >= 21) or (luna == 6 and zi <= 20): return "Gemeni"
    elif (luna == 6 and zi >= 21) or (luna == 7 and zi <= 22): return "Rac"
    elif (luna == 7 and zi >= 23) or (luna == 8 and zi <= 22): return "Leu"
    elif (luna == 8 and zi >= 23) or (luna == 9 and zi <= 22): return "Fecioară"
    elif (luna == 9 and zi >= 23) or (luna == 10 and zi <= 22): return "Balanță"
    elif (luna == 10 and zi >= 23) or (luna == 11 and zi <= 21): return "Scorpion"
    elif (luna == 11 and zi >= 22) or (luna == 12 and zi <= 21): return "Săgetător"
    elif (luna == 12 and zi >= 22) or (luna == 1 and zi <= 19): return "Capricorn"
    elif (luna == 1 and zi >= 20) or (luna == 2 and zi <= 18): return "Vărsător"
    else: return "Pești"

class MakeLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = 'left'
        self.valign = 'middle'
        self.bind(size=self._update_text_size)

    def _update_text_size(self, instance, value):
        self.text_size = value

# ==================== POPUP CALENDAR SELECTOR ====================
class CalendarPopup(Popup):
    def __init__(self, target_input, **kwargs):
        super().__init__(**kwargs)
        self.target_input = target_input
        self.title = "Alege o dată"
        self.size_hint = (0.9, 0.65)

        try:
            init_date = datetime.strptime(target_input.text.strip(), "%d.%m.%Y").date()
        except ValueError:
            init_date = datetime.now().date()

        self.current_year = init_date.year
        self.current_month = init_date.month

        layout = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(5))

        # Navigare lună/an
        nav = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        btn_prev = Button(text="<", size_hint_x=0.2, font_size=sp(16), bold=True)
        btn_prev.bind(on_press=self.prev_month)
        
        self.lbl_month = Label(text="", font_size=sp(15), bold=True)
        
        btn_next = Button(text=">", size_hint_x=0.2, font_size=sp(16), bold=True)
        btn_next.bind(on_press=self.next_month)
        
        nav.add_widget(btn_prev)
        nav.add_widget(self.lbl_month)
        nav.add_widget(btn_next)
        layout.add_widget(nav)

        # Zile săptămână
        days_hdr = GridLayout(cols=7, size_hint_y=None, height=dp(25))
        for d in ["L", "M", "M", "J", "V", "S", "D"]:
            days_hdr.add_widget(Label(text=d, bold=True, font_size=sp(12)))
        layout.add_widget(days_hdr)

        # Grilă zile
        self.grid_days = GridLayout(cols=7, spacing=dp(2))
        layout.add_widget(self.grid_days)

        self.content = layout
        self.render_grid()

    def prev_month(self, instance):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.render_grid()

    def next_month(self, instance):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.render_grid()

    def render_grid(self):
        self.grid_days.clear_widgets()
        self.lbl_month.text = f"{LUNI_RO_LIST[self.current_month-1]} {self.current_year}"
        month_matrix = calendar.monthcalendar(self.current_year, self.current_month)

        for week in month_matrix:
            for day in week:
                if day == 0:
                    self.grid_days.add_widget(Label(text=""))
                else:
                    btn = Button(text=str(day), font_size=sp(13))
                    btn.bind(on_press=lambda inst, d=day: self.pick_date(d))
                    self.grid_days.add_widget(btn)

    def pick_date(self, day):
        d = date(self.current_year, self.current_month, day)
        self.target_input.text = d.strftime("%d.%m.%Y")
        self.dismiss()

# ==================== APLICAȚIA PRINCIPALĂ ====================
class DateCalculatorApp(App):
    def build(self):
        panel = TabbedPanel(
            do_default_tab=False,
            tab_height=dp(48)
        )
        
        tab1 = TabbedPanelHeader(text='Calculator')
        tab1.content = self.create_calculator_tab()
        panel.add_widget(tab1)
        
        tab2 = TabbedPanelHeader(text='Diferență')
        tab2.content = self.create_diferenta_tab()
        panel.add_widget(tab2)

        tab3 = TabbedPanelHeader(text='Calendar')
        tab3.content = self.create_calendar_tab()
        panel.add_widget(tab3)

        tab4 = TabbedPanelHeader(text='Adună/Scade')
        tab4.content = self.create_operatii_tab()
        panel.add_widget(tab4)

        return panel

    # ==================== TAB 1: CALCULATOR ====================
    def create_calculator_tab(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        
        input_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(5))
        input_layout.add_widget(MakeLabel(text="Data:", size_hint_x=0.2, font_size=sp(15)))
        
        self.calc_date_input = TextInput(
            text=datetime.now().strftime("%d.%m.%Y"),
            multiline=False,
            font_size=sp(15),
            padding=[dp(8), dp(10)]
        )
        input_layout.add_widget(self.calc_date_input)

        btn_pop = Button(text="[31]", size_hint_x=None, width=dp(52), font_size=sp(14), bold=True)
        btn_pop.bind(on_press=lambda x: CalendarPopup(self.calc_date_input).open())
        input_layout.add_widget(btn_pop)
        
        btn_today = Button(text="Azi", size_hint_x=0.2, font_size=sp(14))
        btn_today.bind(on_press=lambda x: setattr(self.calc_date_input, 'text', datetime.now().strftime("%d.%m.%Y")))
        input_layout.add_widget(btn_today)
        layout.add_widget(input_layout)

        btn_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        btn_calc = Button(text="Calculează", font_size=sp(15), bold=True)
        btn_calc.bind(on_press=self.calculeaza_data)
        btn_layout.add_widget(btn_calc)

        btn_copy = Button(text="Copiază", font_size=sp(15))
        btn_copy.bind(on_press=lambda x: self.copiaza_text(self.calc_result.text))
        btn_layout.add_widget(btn_copy)
        layout.add_widget(btn_layout)

        scroll = ScrollView()
        self.calc_result = Label(
            text="Introduceți data de referință și apăsați Calculează.",
            halign='center',
            valign='middle',
            font_size=sp(15),
            size_hint_y=None,
            height=dp(200)
        )
        self.calc_result.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        scroll.add_widget(self.calc_result)
        layout.add_widget(scroll)
        
        return layout

    def calculeaza_data(self, instance):
        try:
            data_selectata = datetime.strptime(self.calc_date_input.text.strip(), "%d.%m.%Y").date()
            azi = datetime.now().date()
            diferenta_zile = abs((azi - data_selectata).days)
            
            if data_selectata <= azi:
                rd = relativedelta(azi, data_selectata)
                sens = "Au trecut"
            else:
                rd = relativedelta(data_selectata, azi)
                sens = "Mai sunt"
                
            ziua = ZILE_RO[data_selectata.strftime("%A")]
            saptamana = data_selectata.isocalendar().week
            
            text = (
                f"Data: {data_selectata:%d.%m.%Y}\n"
                f"Ziua săptămânii: {ziua}\n\n"
                f"{sens}:\n"
                f"{rd.years} ani, {rd.months} luni, {rd.days} zile\n\n"
                f"Total zile: {diferenta_zile}\n"
                f"Săptămâna ISO: {saptamana}"
            )
            self.calc_result.text = text
            self.calc_result.height = max(dp(200), self.calc_result.texture_size[1] + dp(20))
        except ValueError:
            self.calc_result.text = "Eroare: Folosiți formatul ZZ.LL.AAAA\n(ex: 25.12.2024)"

    # ==================== TAB 2: DIFERENȚĂ ====================
    def create_diferenta_tab(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        
        row1 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(5))
        row1.add_widget(MakeLabel(text="Data 1:", size_hint_x=0.22, font_size=sp(15)))
        self.dif_d1 = TextInput(text=datetime.now().strftime("%d.%m.%Y"), multiline=False, font_size=sp(15), padding=[dp(8), dp(10)])
        row1.add_widget(self.dif_d1)
        btn_pop1 = Button(text="[31]", size_hint_x=None, width=dp(52), font_size=sp(14), bold=True)
        btn_pop1.bind(on_press=lambda x: CalendarPopup(self.dif_d1).open())
        row1.add_widget(btn_pop1)
        layout.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(5))
        row2.add_widget(MakeLabel(text="Data 2:", size_hint_x=0.22, font_size=sp(15)))
        self.dif_d2 = TextInput(text=datetime.now().strftime("%d.%m.%Y"), multiline=False, font_size=sp(15), padding=[dp(8), dp(10)])
        row2.add_widget(self.dif_d2)
        btn_pop2 = Button(text="[31]", size_hint_x=None, width=dp(52), font_size=sp(14), bold=True)
        btn_pop2.bind(on_press=lambda x: CalendarPopup(self.dif_d2).open())
        row2.add_widget(btn_pop2)
        layout.add_widget(row2)

        btn_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        btn_calc = Button(text="Calculează", font_size=sp(15), bold=True)
        btn_calc.bind(on_press=self.calculeaza_diferenta)
        btn_layout.add_widget(btn_calc)

        btn_copy = Button(text="Copiază", font_size=sp(15))
        btn_copy.bind(on_press=lambda x: self.copiaza_text(self.dif_result.text))
        btn_layout.add_widget(btn_copy)
        layout.add_widget(btn_layout)

        scroll = ScrollView()
        self.dif_result = Label(text="Introduceți datele de referință.", halign='center', valign='middle', font_size=sp(15), size_hint_y=None, height=dp(200))
        self.dif_result.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        scroll.add_widget(self.dif_result)
        layout.add_widget(scroll)
        
        return layout

    def calculeaza_diferenta(self, instance):
        try:
            d1 = datetime.strptime(self.dif_d1.text.strip(), "%d.%m.%Y").date()
            d2 = datetime.strptime(self.dif_d2.text.strip(), "%d.%m.%Y").date()
            if d1 > d2: d1, d2 = d2, d1
            
            rd = relativedelta(d2, d1)
            total = (d2 - d1).days
            
            # Calcul zile lucrătoare (Luni - Vineri)
            cur = d1
            zile_lucratoare = 0
            while cur < d2:
                if cur.weekday() < 5:  # 0=Luni, 1=Marți, 2=Miercuri, 3=Joi, 4=Vineri
                    zile_lucratoare += 1
                cur += timedelta(days=1)
            
            text = (
                f"Data 1: {d1:%d.%m.%Y}\nData 2: {d2:%d.%m.%Y}\n\n"
                f"Diferență:\n{rd.years} ani, {rd.months} luni, {rd.days} zile\n\n"
                f"Zile lucrătoare: {zile_lucratoare}\n"
                f"Total zile calendaristice: {total}"
            )
            self.dif_result.text = text
            self.dif_result.height = max(dp(200), self.dif_result.texture_size[1] + dp(20))
        except ValueError:
            self.dif_result.text = "Eroare: Folosiți formatul ZZ.LL.AAAA"

    # ==================== TAB 3: CALENDAR (INTERACTIV) ====================
    def create_calendar_tab(self):
        main_scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        self.cal_current_year = datetime.now().year
        self.cal_current_month = datetime.now().month
        self.selected_day = datetime.now().day

        nav_box = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(5))
        btn_prev = Button(text="<", size_hint_x=0.18, font_size=sp(18), bold=True)
        btn_prev.bind(on_press=self.cal_prev_month)
        nav_box.add_widget(btn_prev)

        self.lbl_cal_header = Label(
            text=f"{LUNI_RO_LIST[self.cal_current_month-1]} {self.cal_current_year}",
            font_size=sp(16),
            bold=True
        )
        nav_box.add_widget(self.lbl_cal_header)

        btn_next = Button(text=">", size_hint_x=0.18, font_size=sp(18), bold=True)
        btn_next.bind(on_press=self.cal_next_month)
        nav_box.add_widget(btn_next)
        layout.add_widget(nav_box)

        days_header = GridLayout(cols=7, size_hint_y=None, height=dp(28), spacing=dp(2))
        for d in ["L", "M", "M", "J", "V", "S", "D"]:
            days_header.add_widget(Label(text=d, bold=True, font_size=sp(13)))
        layout.add_widget(days_header)

        self.grid_calendar_days = GridLayout(cols=7, size_hint_y=None, height=dp(210), spacing=dp(3))
        layout.add_widget(self.grid_calendar_days)

        row_jump = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(5))
        row_jump.add_widget(MakeLabel(text="An:", size_hint_x=0.15, font_size=sp(13)))
        self.entry_an = TextInput(text=str(self.cal_current_year), multiline=False, input_filter='int', input_type='number', font_size=sp(13), size_hint_x=0.25)
        row_jump.add_widget(self.entry_an)
        
        row_jump.add_widget(MakeLabel(text="Luna:", size_hint_x=0.2, font_size=sp(13)))
        self.combo_luna = Spinner(text=LUNI_RO_LIST[self.cal_current_month-1], values=LUNI_RO_LIST, font_size=sp(12), size_hint_x=0.4)
        row_jump.add_widget(self.combo_luna)

        btn_salt_luna = Button(text="Salt", size_hint_x=0.25, font_size=sp(13))
        btn_salt_luna.bind(on_press=self.salt_la_luna_an)
        row_jump.add_widget(btn_salt_luna)
        layout.add_widget(row_jump)

        row_data = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(5))
        row_data.add_widget(MakeLabel(text="Data:", size_hint_x=0.2, font_size=sp(13)))
        self.entry_data_salt = TextInput(text=datetime.now().strftime("%d.%m.%Y"), multiline=False, font_size=sp(13), size_hint_x=0.45)
        row_data.add_widget(self.entry_data_salt)
        
        btn_pop_cal_tab = Button(text="[31]", size_hint_x=None, width=dp(48), font_size=sp(13), bold=True)
        btn_pop_cal_tab.bind(on_press=lambda x: CalendarPopup(self.entry_data_salt).open())
        row_data.add_widget(btn_pop_cal_tab)

        btn_salt_data = Button(text="Salt la data", size_hint_x=0.25, font_size=sp(13))
        btn_salt_data.bind(on_press=self.salt_la_data)
        row_data.add_widget(btn_salt_data)
        layout.add_widget(row_data)

        row_btns = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        btn_azi = Button(text="Astăzi", font_size=sp(14))
        btn_azi.bind(on_press=self.calendar_azi)
        row_btns.add_widget(btn_azi)

        btn_copiaza_cal = Button(text="Copiază", font_size=sp(14))
        btn_copiaza_cal.bind(on_press=lambda x: self.copiaza_text(self.info_calendar.text))
        row_btns.add_widget(btn_copiaza_cal)
        layout.add_widget(row_btns)

        self.info_calendar = Label(
            text="",
            halign='center',
            valign='middle',
            font_size=sp(14),
            size_hint_y=None,
            height=dp(160)
        )
        self.info_calendar.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        layout.add_widget(self.info_calendar)

        self.render_calendar_grid()
        self.actualizeaza_detalii_text(datetime.now().date())

        main_scroll.add_widget(layout)
        return main_scroll

    def render_calendar_grid(self):
        self.grid_calendar_days.clear_widgets()
        self.lbl_cal_header.text = f"{LUNI_RO_LIST[self.cal_current_month-1]} {self.cal_current_year}"
        
        month_matrix = calendar.monthcalendar(self.cal_current_year, self.cal_current_month)
        today = datetime.now().date()

        for week in month_matrix:
            for day in week:
                if day == 0:
                    self.grid_calendar_days.add_widget(Label(text=""))
                else:
                    is_selected = (day == self.selected_day)
                    is_today = (self.cal_current_year == today.year and self.cal_current_month == today.month and day == today.day)
                    
                    btn_text = f"[{day}]" if is_selected else str(day)
                    btn = Button(
                        text=btn_text,
                        font_size=sp(13),
                        bold=(is_selected or is_today)
                    )
                    btn.bind(on_press=lambda instance, d=day: self.select_day(d))
                    self.grid_calendar_days.add_widget(btn)

    def select_day(self, day):
        self.selected_day = day
        sel_date = date(self.cal_current_year, self.cal_current_month, self.selected_day)
        self.entry_data_salt.text = sel_date.strftime("%d.%m.%Y")
        self.render_calendar_grid()
        self.actualizeaza_detalii_text(sel_date)

    def cal_prev_month(self, instance):
        if self.cal_current_month == 1:
            self.cal_current_month = 12
            self.cal_current_year -= 1
        else:
            self.cal_current_month -= 1
        self.selected_day = 1
        self.entry_an.text = str(self.cal_current_year)
        self.combo_luna.text = LUNI_RO_LIST[self.cal_current_month-1]
        self.select_day(1)

    def cal_next_month(self, instance):
        if self.cal_current_month == 12:
            self.cal_current_month = 1
            self.cal_current_year += 1
        else:
            self.cal_current_month += 1
        self.selected_day = 1
        self.entry_an.text = str(self.cal_current_year)
        self.combo_luna.text = LUNI_RO_LIST[self.cal_current_month-1]
        self.select_day(1)

    def actualizeaza_detalii_text(self, data):
        zi = ZILE_RO[data.strftime("%A")]
        saptamana = data.isocalendar().week
        zi_an = data.timetuple().tm_yday
        zodie = determina_zodie(data.day, data.month)
        bisect = "Da" if calendar.isleap(data.year) else "Nu"
        
        text = (
            f"Data selectată: {data:%d.%m.%Y}\n\n"
            f"Ziua: {zi}\n"
            f"Săptămâna ISO: {saptamana}\n"
            f"Ziua din an: {zi_an}\n"
            f"An bisect: {bisect}\n"
            f"Zodia: {zodie}"
        )
        self.info_calendar.text = text

    def calendar_azi(self, instance):
        azi = datetime.now().date()
        self.cal_current_year = azi.year
        self.cal_current_month = azi.month
        self.selected_day = azi.day
        self.entry_data_salt.text = azi.strftime("%d.%m.%Y")
        self.entry_an.text = str(azi.year)
        self.combo_luna.text = LUNI_RO_LIST[azi.month - 1]
        self.render_calendar_grid()
        self.actualizeaza_detalii_text(azi)

    def salt_la_luna_an(self, instance):
        try:
            an = int(self.entry_an.text.strip())
            luna = LUNI_RO_DICT[self.combo_luna.text]
            self.cal_current_year = an
            self.cal_current_month = luna
            self.selected_day = 1
            d = date(an, luna, 1)
            self.entry_data_salt.text = d.strftime("%d.%m.%Y")
            self.render_calendar_grid()
            self.actualizeaza_detalii_text(d)
        except ValueError:
            self.info_calendar.text = "Eroare: Introduceți un an valid."

    def salt_la_data(self, instance):
        try:
            data = datetime.strptime(self.entry_data_salt.text.strip(), "%d.%m.%Y").date()
            self.cal_current_year = data.year
            self.cal_current_month = data.month
            self.selected_day = data.day
            self.entry_an.text = str(data.year)
            self.combo_luna.text = LUNI_RO_LIST[data.month - 1]
            self.render_calendar_grid()
            self.actualizeaza_detalii_text(data)
        except ValueError:
            self.info_calendar.text = "Eroare: Folosiți formatul ZZ.LL.AAAA"

    # ==================== TAB 4: ADUNĂ / SCADE ====================
    def create_operatii_tab(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        row_base = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        row_base.add_widget(MakeLabel(text="Data inițială:", size_hint_x=0.35, font_size=sp(15)))
        self.op_base_date = TextInput(text=datetime.now().strftime("%d.%m.%Y"), multiline=False, font_size=sp(15), padding=[dp(8), dp(10)])
        row_base.add_widget(self.op_base_date)
        
        btn_pop_op = Button(text="[31]", size_hint_x=None, width=dp(52), font_size=sp(14), bold=True)
        btn_pop_op.bind(on_press=lambda x: CalendarPopup(self.op_base_date).open())
        row_base.add_widget(btn_pop_op)
        layout.add_widget(row_base)

        row_op = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        row_op.add_widget(MakeLabel(text="Operație:", size_hint_x=0.35, font_size=sp(15)))
        self.spinner_op = Spinner(text='Adună', values=('Adună', 'Scade'), font_size=sp(15))
        row_op.add_widget(self.spinner_op)
        layout.add_widget(row_op)

        grid = GridLayout(cols=2, size_hint_y=None, height=dp(180), spacing=dp(8))
        
        grid.add_widget(MakeLabel(text="Ani:", font_size=sp(15)))
        self.spin_ani = TextInput(text='0', multiline=False, input_filter='int', input_type='number', font_size=sp(15), padding=[dp(8), dp(8)])
        grid.add_widget(self.spin_ani)

        grid.add_widget(MakeLabel(text="Luni:", font_size=sp(15)))
        self.spin_luni = TextInput(text='0', multiline=False, input_filter='int', input_type='number', font_size=sp(15), padding=[dp(8), dp(8)])
        grid.add_widget(self.spin_luni)

        grid.add_widget(MakeLabel(text="Săptămâni:", font_size=sp(15)))
        self.spin_saptamani = TextInput(text='0', multiline=False, input_filter='int', input_type='number', font_size=sp(15), padding=[dp(8), dp(8)])
        grid.add_widget(self.spin_saptamani)

        grid.add_widget(MakeLabel(text="Zile:", font_size=sp(15)))
        self.spin_zile = TextInput(text='0', multiline=False, input_filter='int', input_type='number', font_size=sp(15), padding=[dp(8), dp(8)])
        grid.add_widget(self.spin_zile)
        
        layout.add_widget(grid)

        btn_layout = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        btn_calc = Button(text="Calculează", font_size=sp(15), bold=True)
        btn_calc.bind(on_press=self.calculeaza_operatie)
        btn_layout.add_widget(btn_calc)

        btn_copy = Button(text="Copiază", font_size=sp(15))
        btn_copy.bind(on_press=lambda x: self.copiaza_text(self.op_result.text))
        btn_layout.add_widget(btn_copy)
        layout.add_widget(btn_layout)

        scroll = ScrollView()
        self.op_result = Label(text="Introduceți valorile dorite.", halign='center', valign='middle', font_size=sp(15), size_hint_y=None, height=dp(180))
        self.op_result.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        scroll.add_widget(self.op_result)
        layout.add_widget(scroll)

        return layout

    def calculeaza_operatie(self, instance):
        try:
            data_baza = datetime.strptime(self.op_base_date.text.strip(), "%d.%m.%Y").date()
            ani = int(self.spin_ani.text.strip() or 0)
            luni = int(self.spin_luni.text.strip() or 0)
            saptamani = int(self.spin_saptamani.text.strip() or 0)
            zile = int(self.spin_zile.text.strip() or 0)
            
            delta = relativedelta(years=ani, months=luni, weeks=saptamani, days=zile)
            
            if self.spinner_op.text == "Adună":
                rezultat = data_baza + delta
                operatie = "Adunare"
            else:
                rezultat = data_baza - delta
                operatie = "Scădere"
                
            zi = ZILE_RO[rezultat.strftime("%A")]
            zodie = determina_zodie(rezultat.day, rezultat.month)
            
            text = (
                f"Data inițială: {data_baza:%d.%m.%Y}\n"
                f"Operație: {operatie}\n"
                f"Data finală: {rezultat:%d.%m.%Y}\n\n"
                f"Ziua: {zi} | Zodia: {zodie}\n"
                f"Săptămâna ISO: {rezultat.isocalendar().week}"
            )
            self.op_result.text = text
            self.op_result.height = max(dp(180), self.op_result.texture_size[1] + dp(20))
        except ValueError:
            self.op_result.text = "Eroare: Verificați formatul datei (ZZ.LL.AAAA)"

    def copiaza_text(self, text):
        Clipboard.copy(text)

if __name__ == "__main__":
    DateCalculatorApp().run()
