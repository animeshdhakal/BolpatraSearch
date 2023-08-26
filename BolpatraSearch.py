from tkinter import *
from tkinter.ttk import *
import requests
import urllib3
from bs4 import BeautifulSoup
import webbrowser
from _thread import start_new_thread

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    pass

root = Tk()


class TreeViewEdit(Treeview):
    def __init__(self, master, **kw):
        Treeview.__init__(self, master, **kw)

        self.editwin = None
        self.editable_columns = []

        self.bind("<Button-1>", self.click, True)
        self.bind("<Double-Button-1>", self.double_click, True)

    def click(self, event):
        item = self.identify("item", event.x, event.y)

        col_index = int(self.identify_column(event.x).replace("#", "")) - 1

        root.clipboard_clear()
        root.clipboard_append(self.item(item)["values"][col_index])

    def double_click(self, event):
        item = self.identify("item", event.x, event.y)

        url = f"https://www.bolpatra.gov.np/egp/getTenderDetails?tenderId={self.item(item)['values'][1]}"

        webbrowser.open(url)


class UI:
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.frame.pack()

        self.search_label = Label(self.frame, text="Search")
        self.search_label.pack(side=LEFT)

        self.search_entry = Entry(self.frame)
        self.search_entry.pack(side=LEFT)

        self.search_button = Button(
            self.frame, text="Search", command=self.startSearch)
        self.search_button.pack(side=LEFT)

        self.tv = TreeViewEdit(self.master, show="headings", height=35)

        self.verscrlbar = Scrollbar(self.frame,
                           orient ="vertical",
                           command = self.tv.yview)
        self.tv.configure(xscrollcommand = self.verscrlbar.set)
       

        self.tv['columns'] = (1, 2, 3, 4, 5, 6, 7)

        self.tv.heading(1, text="S.N.")
        self.tv.heading(2, text='Tender ID')
        self.tv.heading(3, text='Code')

        self.tv.column(1, width=100)
        self.tv.column(2, width=100)
        self.tv.column(3, width=200)
        self.tv.column(4, width=600)
        self.tv.column(7, width=100)

        self.tv.heading(4, text='Title')
        self.tv.heading(5, text='Published Date')
        self.tv.heading(6, text='Closing Date')
        self.tv.heading(7, text='Remaning Days')

        self.tv.pack()

    def startSearch(self):
        start_new_thread(self.search, ())

    def search(self):
        self.search_button.config(state=DISABLED)

        self.tv.delete(*self.tv.get_children())

        self.tv.insert('', 'end', values=('', '', '', 'Searching...',))

        search = self.search_entry.get()

        page = 1
        sn = 1

        firstFound = True

        while True:
            URL = f"https://www.bolpatra.gov.np/egp/searchBidDashboardHomePage?bidSearchTO.title={search}&currentPageIndexInput={page}&pageActionInput=goto&pageSizeInput=30"

            res = requests.get(URL, timeout=30)

            soup = BeautifulSoup(res.text, 'lxml')

            no_result = soup.find('label', id='No Result found')

            if no_result:
                break

            trs = soup.find_all('tr')

            for tr in trs[1:]:
                tds = tr.find_all('td')

                tenderId = tds[2].find('a').get('onclick').split("'")[1]
                code = tds[1].text.strip()
                title = tds[2].text.strip()
                published_date = tds[6].text.strip()
                closing_date = tds[7].text.strip()
                remaning_days = tds[8].text.strip()

                if remaning_days != 'Expired':
                    if firstFound:
                        self.tv.delete(*self.tv.get_children())
                        firstFound = False

                    self.tv.insert('', 'end', values=(
                        sn, tenderId, code, title, published_date, closing_date, remaning_days))

                    sn += 1

            page += 1

        if not self.tv.get_children():
            self.tv.insert('', '', 'end', values=('', '', 'No Result Found',))

        self.search_button.config(state=NORMAL)


ui = UI(root)

root.title("Bolpatra Search")
root.state("zoomed")

root.mainloop()
