from datetime import datetime
from platform import release
from socket import socket
import Pyro4
import Pyro4.core
import os
import threading
import time

from Pyro5.client import Proxy

items_for_sale = ['bicycle', 'lamp', 'tv']
account_dict = {'admin,admin':{}}
current_customers = []
sem = [1]

@Pyro4.expose
class Store(object):
    def __init__(self):
        self.sem = Sempaphore()
        self.items_for_sale = items_for_sale

    def browse(self):
        return items_for_sale
    
    def buy_item(self, item, username, password):
        self.sem.wait()
        account = ','.join([username, password])
        try:
            if item in self.items_for_sale:
                self.items_for_sale.remove(item)
                print(f"{item} was purchased by {account}!")
                print(f"Inventory: {items_for_sale}")
                return f'Enjoy your {item}!'
            else:
                return f"We are sorry, '{item}' is not in stock."
        finally:
            self.sem.signal()


    # This is a tester function for testing the semaphore. It's idential to buy_item() except it also includes a
    def buy_item_sleep(self, item, username, password):
        self.sem.wait()
        time.sleep(10)
        account = ','.join([username, password])
        try:
            if item in items_for_sale:
                items_for_sale.remove(item)
                print(f"{item} was purchased by {account}!")
                print(f"Inventory: {items_for_sale}")
                return f'Enjoy your {item}!'
            else:
                return f"We are sorry, '{item}' is not in stock."
        finally:
            self.sem.signal()

    def check_account_exists(self, username, password):
        if ','.join([username, password]) in account_dict:
            return True
        else:
            return False

    def create_account(self, username, password):
        account = ','.join([username, password])
        account_dict[account] = {}
        print(f'Customer account has been created. Username: "{username}" and Password: "{password}"')
        print(f'All accounts: {[x for x in account_dict.keys()]}')

    def add_current_customer(self, username, password):
        account = ','.join([username, password])
        current_customers.append(account)
        print(f'Customer entered the shop: {account}')
        print(f'Accounts currently shopping: {[x for x in current_customers]}')
    
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
        print(f'Accounts currently shopping: {[x for x in current_customers]}')


####################

class Naming_Server(threading.Thread):
    def run(self):
        os.system("python -m Pyro4.naming")

#####################

class Sempaphore():
    def __init__(self):
        self.sem = sem

    def wait(self):
        while(True):
            if self.sem[0] >= 1:
                self.sem[0] -= 1
                break

    def signal(self):
        self.sem[0] += 1

#######################

def start_server():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(Store)
    ns.register('store.server', str(uri))
    print(f'\nOpen For Business!')
    print(f"Customer Accounts: {[x for x in account_dict.keys()]}")
    print(f"Inventory: {items_for_sale}")
    daemon.requestLoop()


if __name__ == '__main__':
    try:
        print("Starting up server...")
        thread = Naming_Server()
        thread.start()
        start_server()
    except (KeyboardInterrupt, EOFError):
        print("Sorry We're Closed!")