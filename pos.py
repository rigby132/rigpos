# Simple point of sale system!
# By Rigby132
# Copyright (c) 2022

from datetime import date
import json
import codecs
import tkinter as tk
import tkinter.font
from tkinter import ttk
from tkinter import messagebox

MIN_WIDTH = 800
MIN_HEIGHT = 600
FONT_SIZE = 30
INVENTORY_PATH = "./inventory.csv"
LOG_PATH = "./toplam.json"
LANG_PATH = "./lang.json"

# Important vars
inventory = {}
lang = {"code": "Code",
        "total": "Total",
        "day_total": "Daily total",
        "sell": "Sell",
        "long_code": "Scancode too long.",
        "not_in_inventory": "Not in inventory.",
        "currency": "€",
        "set_amount": "Set amount.",
        "quantity": "Qty",
        "price": "Price",
        "name": "Name",
        "not_number": "Amount must be a positive number"}
shopping_list = {}


def get_day_total():
    f = codecs.open(LOG_PATH, "r", encoding="utf-8")
    log = json.load(f)
    f.close()

    today = date.today().isoformat()

    if today in log:
        return log[today]
    else:
        return 0


def log_month_total():
    f = codecs.open(LOG_PATH, "r", encoding="utf-8")
    log = json.load(f)
    f.close()

    month = date.today().isoformat()[:-3]

    total_month = 0

    for day in log.keys():
        if day[:-3] == month:
            total_month += log[day]

    log[month] = total_month

    log = dict(sorted(log.items()))

    f = codecs.open(LOG_PATH, "w", encoding="utf-8")
    json.dump(log, f, indent=4)
    f.close()


def log_sale(total):
    f = codecs.open(LOG_PATH, "r", encoding="utf-8")
    log = json.load(f)
    f.close()

    today = date.today().isoformat()

    if today in log:
        log[today] += total
    else:
        log[today] = total

    log = dict(sorted(log.items()))

    f = codecs.open(LOG_PATH, "w", encoding="utf-8")
    json.dump(log, f, indent=4)
    f.close()


def convert_int_to_price(value):
    value_str = str(value)
    value_str = '0'*(3 - len(value_str)) + value_str
    value_str = value_str[:-2] + '.' + value_str[-2:]
    return value_str + lang["currency"]


def load_lang():
    f = codecs.open(LANG_PATH, "r", encoding="utf-8")

    global lang
    lang = json.load(f)

    f.close()


def load_inventory():
    f = codecs.open(INVENTORY_PATH, "r", encoding="utf-8")
    global inventory
    inventory = {}

    f.readline()

    i = 0
    for line in f.readlines():
        i+=1
        try:
            code, name, price, stock = line.strip('\n').split(sep=',')
        except ValueError:
            print("Could not read line:", i)

        price = int(price)
        stock = int(stock)
        inventory[code] = [name, price, stock]

    f.close()


def save_inventory():
    f = codecs.open(INVENTORY_PATH, "wb", encoding="utf-8")
    f.write("code,name,price,stock\n")
    for code in inventory:
        f.write(code + "," + inventory[code][0] + "," + str(inventory[code][1]) + "," + str(inventory[code][2]) + '\n')
    f.close()


def get_total():
    total = 0
    for code in shopping_list:
        amount = shopping_list[code]
        total += inventory[code][1] * amount
    return total


def setup_ui(root):
    # ==========================
    # SHOPPING LIST
    # ==========================
    list_frame = tk.Frame(root)
    list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nwes")

    list_frame.columnconfigure(0, weight=1)
    list_frame.rowconfigure(0, weight=1)

    shopping_items = tk.StringVar()

    treeview = ttk.Treeview(list_frame)

    treeview["columns"] = ("quantity", "price", "name", "code")
    treeview.column('#0', width=0, stretch="no")
    treeview.column("quantity", anchor="center", width=30)
    treeview.column("price", anchor="center", width=50)
    treeview.column("name", anchor="center", width=200)
    treeview.column("code", anchor="center", width=100)

    treeview.heading('#0', text='', anchor="center")
    treeview.heading("quantity", text=lang["quantity"], anchor="center")
    treeview.heading("price", text=lang["price"], anchor="center")
    treeview.heading("name", text=lang["name"], anchor="center")
    treeview.heading("code", text=lang["code"], anchor="center")

    treeview.grid(
        column=0,
        row=0,
        sticky='nwes'
    )

    scrollbar = ttk.Scrollbar(
        list_frame,
        orient='vertical',
        command=treeview.yview
    )

    treeview['yscrollcommand'] = scrollbar.set

    scrollbar.grid(
        column=1,
        row=0,
        sticky='ns')

    # ==========================
    # OPTIONS
    # ==========================
    options_frame = tk.Frame(root)
    options_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nwes")

    options_frame.columnconfigure(0, weight=1)
    options_frame.rowconfigure(0, weight=1)
    options_frame.rowconfigure(1, weight=1)
    options_frame.rowconfigure(2, weight=1)

    # ENTRY----------------------------------
    entry_frame = tk.Frame(options_frame)

    entry_label = tk.Label(entry_frame, text=lang["code"]+":")

    code_string = tk.StringVar()
    code_entry = ttk.Entry(entry_frame, textvariable=code_string)
    code_entry.focus_set()  # keep code entry always in focus

    entry_label.pack(side=tk.LEFT)
    code_entry.pack(side=tk.RIGHT)

    entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

    # PRICE----------------------------------
    total_label = tk.Label(options_frame, text=lang["total"]+": ")
    total_label.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

    # DAILY TOTAL----------------------------
    day_total_label = tk.Label(options_frame, text=lang["day_total"]+": ")
    day_total_label.grid(row=2, column=0, padx=10, pady=10, sticky="ns")

    def update_day_total():
        # Update day total
        day_total = get_day_total()
        day_total_str = convert_int_to_price(day_total)
        day_total_label.config(text=lang["day_total"] + ": " + day_total_str)


    # CALLBACKS------------------------------
    def update_shopping_list():
        # Update treeview
        treeview.delete(*treeview.get_children())

        for code in shopping_list:
            quantity = str(shopping_list[code])
            price = convert_int_to_price(inventory[code][1])
            name = inventory[code][0]
            # Add ; so it is not converted to a int
            treeview.insert('', tk.END, values=(
                quantity, price, name, code + ";"))

        # Update total
        total = get_total()
        total_str = convert_int_to_price(total)
        total_label.config(text=lang["total"] + ": " + total_str)


    # SALE-----------------------------------
    def apply_sale():
        for code in shopping_list:
            inventory[code][2] -= shopping_list[code]

        log_sale(get_total())
        log_month_total()
        save_inventory()

        shopping_list.clear()
        update_shopping_list()
        update_day_total()

    sell_button = tk.Button(
        options_frame, text=lang["sell"], command=apply_sale)
    sell_button.grid(row=2, column=0, padx=10, pady=10, sticky="wes")

    # Double click on item in shopping list: popup -> set # of items
    def on_shopping_list_click(event):
        if len(treeview.focus()) == 0:
            return

        # Little popup
        top = tk.Toplevel(root)
        top.geometry("250x100")
        top.title(lang["set_amount"])

        entry = tk.Entry(top, width=25)
        entry.pack(pady=10, side=tk.TOP)
        entry.focus_set()

        def on_enter_amount(event=None):
            # get code and remove ";" at the end!
            code = treeview.item(treeview.focus())["values"][3][:-1]
            amount = entry.get()

            if not str.isdigit(amount):
                messagebox.showinfo(
                    "Error", lang["not_number"], parent=top, icon='error')
                return

            amount = int(amount)

            if amount == 0:
                del shopping_list[code]
            else:
                shopping_list[code] = amount

            update_shopping_list()
            top.destroy()
            code_entry.focus_set()

        entry.bind("<Return>", on_enter_amount)
        button = tk.Button(top, text="OK", command=on_enter_amount)
        button.pack(pady=5, side=tk.TOP)

    treeview.bind('<Double-Button>', on_shopping_list_click)

    # Check code callback
    def on_code_return(event):
        code = code_string.get()
        code_string.set("")

        if code not in inventory:
            messagebox.showinfo(
                "Error", lang["not_in_inventory"], icon='error')
            return

        # Add item to shopping list and update
        # Is item already in list?
        if code in shopping_list:
            shopping_list[code] += 1
        else:
            shopping_list[code] = 1

        update_shopping_list()

    #code_string.trace("w", lambda name, index, mode,
    #                  sv=code_string: on_code_modified(sv))
    code_entry.bind("<Return>", on_code_return)

    update_shopping_list()
    update_day_total()


def main():
    """Setup window and run.
    """

    # Load language
    load_lang()

    # Load inventory
    load_inventory()

    root = tk.Tk()
    root.title("POS-SYSTEM")
    root.minsize(MIN_WIDTH, MIN_HEIGHT)
    root.geometry("640x480")

    default_font = tk.font.nametofont("TkDefaultFont")
    default_font.configure(size=FONT_SIZE)
    root.option_add("*Font", default_font)

    root.columnconfigure(0, weight=4)
    root.rowconfigure(0, weight=4)
    root.columnconfigure(1, weight=0)

    setup_ui(root)

    root.mainloop()


if __name__ == "__main__":
    main()
