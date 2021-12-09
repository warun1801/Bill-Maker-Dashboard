from locale import currency
from fpdf import FPDF
import tkinter
from tkinter import font as tkFont
import decimal    

class BillMaker:

    def __init__(self):
        self.date_set = ""
        self.invoice = 0
        self.total = 0
        self.client = ""
        self.pdf = FPDF(orientation="P", unit="mm", format="A4")
        self.pdf.add_page()
        self.pdf.set_font("helvetica", "B", 10)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.image("./Bill Template.png", x=0, y=0, w=210, h=297)

    # private function to change currency to words in Indian rupees
    def _num2words(self, num):
        num = decimal.Decimal(num)
        decimal_part = num - int(num)
        num = int(num)

        if decimal_part:
            return self._num2words(num) + " point " + (" ".join(self._num2words(i) for i in str(decimal_part)[2:]))
        under_20 = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        above_100 = {100: 'Hundred', 1000: 'Thousand', 100000: 'Lakhs', 10000000: 'Crores'}
        if num < 20:
            return under_20[num]
        if num < 100:
            return tens[num // 10 - 2] + ('' if num % 10 == 0 else ' ' + under_20[num % 10])
        # find the appropriate pivot - 'Million' in 3,603,550, or 'Thousand' in 603,550
        pivot = max([key for key in above_100.keys() if key <= num])
        return self._num2words(num // pivot) + ' ' + above_100[pivot] + ('' if num % pivot==0 else ' ' + self._num2words(num % pivot))    

    # function to set address in bill template
    def address_setter(self, txt, name=''):
        txtlist = txt.split("\n")
        y = 72
        if name == '':
            self.client = txtlist[0].strip()
        else:
            self.client = name
        for txt in txtlist:
            self.pdf.text(x=48, y=y, txt=txt.strip())
            y += 3.5
        
        y = 96
        for txt in txtlist:
            self.pdf.text(x=48, y=y, txt=txt.strip())
            y += 3.5

    # function to print single item in bill template
    def single_item(self, txt, y, srno, quantity, rate):
        self.pdf.text(x=21, y = y, txt=str(srno) + '.')
        self.pdf.text(x=127, y=y, txt=str(quantity))
        self.pdf.text(x=142, y=y, txt=str(rate))
        self.pdf.text(x=165, y=y, txt=str(rate * quantity))
        self.total += rate * quantity
        lines = self.line_splitter(txt, 330)
        for line in lines:
            self.pdf.text(x=30, y=y, txt=line)
            y += 3.5
        y-=3.5
        return y

    def item_list(self, items, quantities, rates):
        y = 135
        for item in items:
            y = self.single_item(item, y, items.index(item) + 1, quantities[items.index(item)], rates[items.index(item)])
            y += 10
        self.total = round(self.total, 2)
        self.pdf.text(x=165, y=223, txt=str(self.total))
        gst = round(self.total * 0.09, 2)
        self.pdf.text(x=165, y=232, txt=str(gst))
        self.pdf.text(x=165, y=240, txt=str(gst))
        self.total = round(self.total + 2 * gst, 2)
        self.pdf.text(x=165, y=248, txt=str(self.total))

    def date_setter(self, given_date):
        self.date_set = given_date
        self.pdf.text(x=155, y=112, txt=self.date_set)

    def invoice_setter(self, inv_no):
        self.invoice = inv_no
        self.pdf.text(x=155, y=104, txt=self.invoice)

    def total_currency_words_setter(self):
        currency_in_words = self._num2words(round(self.total)) + " Only"
        actual_lines = self.line_splitter(currency_in_words, 345)
        y = 240.5
        for line in actual_lines:
            self.pdf.text(x=32, y=y, txt=line)
            y += 3.5

    def visual_width(self, text):
        tkinter.Frame().destroy()  # Enough to initialize resources
        txt = tkFont.Font(family="helvetica", size=10, weight="bold")
        width = txt.measure(text)
        return width


    def line_splitter(self, text, size):
        line = ""
        lines = []
        for word in text.split():
            if self.visual_width(line.strip() + " " + word.strip()) > size:
                lines.append(line.strip())
                line = word.strip()
            else:
                line += " " + word.strip()
        lines.append(line.strip())
        return lines

    def set_file_name(self):
        filename = str(self.invoice) + "dt." + str(self.date_set) + "." + self.client + ".pdf"
        return filename


    def multiline_input(self, msg=""):
        lines = []
        if msg:
            print(msg)
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                break
        text = '\n'.join(lines)
        return text

    def bill_maker(self):
        print("\n--------------Bill Maker---------------\n")

        address = self.multiline_input("Enter the address to for billing/shipping: (Press an extra 'Enter' to complete the address)")
        self.address_setter(address)
        print("Address saved\n")

        items = list(self.multiline_input("Enter the item list(Name only each in seperate line):").split('\n'))
        print("Enter the quantities orderwise: (In the same line spaces in between)")
        quantities = list(map(int, input().split()))
        print("Enter the rates orderwise: (In the same line spaces in between)")
        rates = list(map(float, input().split()))
        self.item_list(items, quantities, rates)
        print("Items saved\n")

        date = input("Enter Date:(dd.mm.yyyy format)\n")
        self.date_setter(date)

        invoice = input("Enter Invoice Number:\n")
        self.invoice_setter(invoice)

        self.total_currency_words_setter()
        self.pdf.output(self.set_file_name())
        print("\nBill is generated and saved as: " + self.set_file_name())
        
        print("\n--------------The End---------------\n")

    def bill_maker_form(self, name, address, items, quantities, rates, date, invoice):
        self.address_setter(address, name)
        self.item_list(items, quantities, rates)
        self.date_setter(date)
        self.invoice_setter(invoice)
        self.total_currency_words_setter()
        self.pdf.output(self.set_file_name())
        print("\nBill is generated and saved as: " + self.set_file_name())

