import Pyro4
import Pyro4.core
import os
import threading
import time
import pandas as pd
from datetime import datetime

account_dict = {'admin,admin':{}}
current_customers = []
carts = {}
item_dict ={}


class Store(object):
    def __init__(self):
        self.item_dict = item_dict
        self.carts = carts

    @Pyro4.expose
    def get_inventory(self):
        inventory = ''
        for it in self.item_dict.keys():
            inventory = inventory + it + ": " + str(self.item_dict[it].get_number_in_stock()) + '\n'
        return inventory
    
    @Pyro4.expose
    def buy_item(self, item, username, password, sleep=None):
        if item in self.item_dict.keys():  
            self.item_dict[item].wait()

            # This is for testing the semaphore.
            if sleep:
                time.sleep(sleep)

            account = ','.join([username, password])
            try:
                if self.item_dict[item].get_number_in_stock() > 0:
                    self.item_dict[item].reduce_number_in_stock()
                    print(f"{item} was purchased by {account}!")
                    print(f"Inventory: ")
                    print(self.get_inventory()) 
                    return f'Your {item} has been ordered and will arrive in 1 day.'
                else:
                    return f"We are sorry, we don't have '{item}' in stock right now."
            finally:
                self.item_dict[item].signal()
        else:
            return f"We are sorry, we don't sell '{item}'."

    @Pyro4.expose
    def buy_cart(self, username, password):
        response = ''
        account = ','.join([username, password])
        if account in self.carts:
            for item in self.carts[account].keys():
                for quant in range(self.carts[account][item]):
                    result = self.buy_item(item, username, password)
                    response = response + result + '\n'
            self.carts.pop(account)
            return response
        else:
            return "You don't have any items in your cart."

    @Pyro4.expose
    def view_cart(self, username, password):
        cart = ''
        account = ','.join([username, password])
        if account in self.carts:
            for it in self.carts[account].keys():
                cart = cart + it + ": " + str(self.carts[account][it]) + '\n'
        else:
            cart = "You don't have anything in the cart right now"
        return cart

    @Pyro4.expose
    def cart_item(self, item, username, password, quantity=1):
        if item in self.item_dict.keys():  
            account = ','.join([username, password])
            if self.item_dict[item].get_number_in_stock() > 0:
                if account in self.carts:
                    if item in self.carts[account]:
                        self.carts[account][item] += quantity
                    else:
                        self.carts[account][item] = quantity
                else:
                    self.carts[account] = {item: quantity}
                print(self.carts)
                return f"{quantity} '{item}' added to your cart."
            else:
                return f"We are sorry, we don't have '{item}' in stock right now."
        else:
            return f"We are sorry, we don't sell '{item}'."

    @Pyro4.expose
    def check_account_exists(self, username, password):
        if ','.join([username, password]) in account_dict:
            return True
        else:
            return False

    @Pyro4.expose
    def create_account(self, username, password):
        account = ','.join([username, password])
        account_dict[account] = {}
        print(f'Customer account has been created. Username: "{username}" and Password: "{password}"')
        print(f'All accounts: {[x for x in account_dict.keys()]}\n')

    @Pyro4.expose
    def add_current_customer(self, username, password):
        account = ','.join([username, password])
        current_customers.append(account)
        print(f'Customer entered the shop: {account}')
        print(f'Accounts currently shopping: {[x for x in current_customers]}\n')
    
    @Pyro4.expose
    def check_if_current_shopper(self, username, password):
        account = ','.join([username, password])
        if account in current_customers:
            return True
        else:
            return False
    
    @Pyro4.expose
    def exit_customer(self, username, password):
        account = ','.join([username, password])
        current_customers.remove(account)
        print(f'Customer left the shop: {account}')
        print(f'Accounts currently shopping: {[x for x in current_customers]}\n')

    @Pyro4.expose
    def ping(self):
        return "Customer is entering store."

    def get_initial_inventory(self):
        inventory = ''
        for it in self.item_dict.keys():
            inventory = inventory + it + ": " + str(self.item_dict[it].get_number_in_stock()) + '\n'
        return inventory

    def stock_inventory(self):
        with open('items.txt', 'r') as file:
            for item in file.readlines():
                item = item.strip()
                item_split = item.split(',')
                if len(item_split) != 3:
                    print(f'Item not in correct format in file: {item}. Skipping...')
                    continue
                name = item_split[0]
                quantity = int(item_split[1])
                price = float(item_split[2])
                if name not in self.item_dict:
                    self.item_dict[name] = Item(name, quantity, price)
                else:
                    self.item_dict[name].increase_number_in_stock(quantity)
        print(f'\nOpen For Business!')
        print(f"Customer Accounts: {[x for x in account_dict.keys()]}")
        print(f"Inventory: ")
        print(self.get_initial_inventory(),'\n')


    ### This might be the issue
    def generate_backup_file(self):
        print('test')
        current_time = datetime.now()
        print('test')
        current_time = current_time.strftime('%H:%M:%S')
        print(current_time)
        print('test')
        path = 'backups'
        if not os.path.exists(path):
            os.mkdir(path)
        print('test')
        file_path = f'{path}/backup_{current_time}.txt'
        print(file_path)
        with open(file_path, 'w') as file:
            print('test1')
            file.write(str(account_dict))
            print('test2')




####################

class Naming_Server(threading.Thread):
    def run(self):
        os.system("python -m Pyro4.naming")


#######################

class Item():
    def __init__(self, item_name, quantity, price):
        self.sem = 1
        self.item_name = item_name
        self.number_in_stock = int(quantity)
        self.price = float(price)

    def get_item_name(self):
        return self.item_name

    def get_price(self):
        return self.price

    def get_number_in_stock(self):
        return self.number_in_stock

    def reduce_number_in_stock(self):
        self.number_in_stock -= 1

    def increase_number_in_stock(self, quantity=1):
        self.number_in_stock += quantity

    def wait(self):
        while(True):
            if self.sem >= 1:
                self.sem -= 1
                break

    def signal(self):
        self.sem += 1
    

#######################


def stock_inventory():
    with open('items.txt', 'r') as file:
        for item in file.readlines():
            item = item.strip()
            item_split = item.split(',')
            if len(item_split) != 3:
                print(f'Item not in correct format in file: {item}. Skipping...')
                continue
            name = item_split[0]
            quantity = int(item_split[1])
            price = float(item_split[2])
            if name not in item_dict:
                item_dict[name] = Item(name, quantity, price)
            else:
                item_dict[name].increase_number_in_stock(quantity)
    print(f'\nOpen For Business!')
    print(f"Customer Accounts: {[x for x in account_dict.keys()]}")
    print(f"Inventory: ")
    print(get_initial_inventory(),'\n')


def get_initial_inventory():
    inventory = ''
    for it in item_dict.keys():
        inventory = inventory + it + ": " + str(item_dict[it].get_number_in_stock()) + '\n'
    return inventory


def start_server():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(Store)
    ns.register('store.server', str(uri))
    stock_inventory()
    daemon.requestLoop()


if __name__ == '__main__':
    try:
        print("Starting up server...")
        thread = Naming_Server()
        thread.start()
        start_server()
    except (KeyboardInterrupt, EOFError):
        print("Sorry We're Closed!")