import Pyro4
import Pyro4.core
import os
import threading
import time
import pandas as pd

account_dict = {'admin,admin':{}}
current_customers = []
item_dict = {}

@Pyro4.expose
class Store(object):
    def __init__(self):
        self.item_dict = item_dict

    def get_inventory(self):
        inventory = ''
        for it in self.item_dict.keys():
            inventory = inventory + it + ": " + str(self.item_dict[it].get_number_in_stock()) + '\n'
        return inventory
    
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
                    return f'Enjoy your {item}!'
                else:
                    return f"We are sorry, we don't have '{item}' in stock right now."
            finally:
                self.item_dict[item].signal()
        else:
            return f"We are sorry, we don't sell '{item}'."


    def check_account_exists(self, username, password):
        if ','.join([username, password]) in account_dict:
            return True
        else:
            return False

    def create_account(self, username, password):
        account = ','.join([username, password])
        account_dict[account] = {}
        print(f'Customer account has been created. Username: "{username}" and Password: "{password}"')
        print(f'All accounts: {[x for x in account_dict.keys()]}\n')

    def add_current_customer(self, username, password):
        account = ','.join([username, password])
        current_customers.append(account)
        print(f'Customer entered the shop: {account}')
        print(f'Accounts currently shopping: {[x for x in current_customers]}\n')
    
    def check_if_current_shopper(self, username, password):
        account = ','.join([username, password])
        if account in current_customers:
            return True
        else:
            return False
    
    def exit_customer(self, username, password):
        account = ','.join([username, password])
        current_customers.remove(account)
        print(f'Customer left the shop: {account}')
        print(f'Accounts currently shopping: {[x for x in current_customers]}\n')

    def ping(self):
        return "Customer is entering store."


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
    print(f'\nOpen For Business!')
    print(f"Customer Accounts: {[x for x in account_dict.keys()]}")
    print(f"Inventory: ")
    print(get_initial_inventory(),'\n')
    daemon.requestLoop()


if __name__ == '__main__':
    try:
        print("Starting up server...")
        thread = Naming_Server()
        thread.start()
        stock_inventory()
        start_server()
    except (KeyboardInterrupt, EOFError):
        print("Sorry We're Closed!")