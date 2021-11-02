import Pyro4
import argparse

global username
global password

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='username', action='store')
    parser.add_argument('-p', dest='password', action='store')
    parser.add_argument('-shopped', dest='shopped', action='store', default='n')
    parser.add_argument('-server', dest='server', action='store')
    
    args = parser.parse_args()
    return args


class Customer(object):
    def __init__(self, args):
        self.args = args
        if not self.args.server:
            self.Storefront = Pyro4.Proxy(f"PYRONAME:store.server")
        else:
            self.Storefront = Pyro4.Proxy(self.args.server)

    def start_shopping(self):
        try:
            self.Storefront.ping()
            text = ''
            can_enter = False
            user_pass_preset = False
            username = ''
            password = ''

            if self.args.username and self.args.password:
                user_pass_preset = True
            while (text.lower() != 'y' and text.lower() != 'n' and not can_enter):
                if not user_pass_preset:
                    text = input('Have you shopped with us before? (y/n)')
                    text = text.lower()
                    self.args.shopped = text
                    if text == 'n':
                        print('Please create an account')
                    elif text == 'y':
                        print('Please login')
                    else:
                        continue
                while (not can_enter):
                    if not user_pass_preset:
                        username = input('Username: ')
                        password = input('Password: ')
                    else:
                        username = self.args.username
                        password = self.args.password
                    is_exists = self.Storefront.check_account_exists(username, password)
                    is_shopping = self.Storefront.check_if_current_shopper(username, password)
                    if text == 'y' or self.args.shopped.lower() == 'y':
                        if not is_exists:
                            print(f"Sorry, no account exists with Username: '{username}' and Password: '{password}'.\n")
                        else:
                            if not is_shopping:
                                print('Welcome to the store!\n')
                                can_enter = True
                            else:
                                print('We are sorry, someone already appears to be logged on with that account. Please try another account.')
                    elif text == 'n' or self.args.shopped.lower() == 'n':
                        if is_exists:
                            if is_shopping:
                                print('We are sorry, someone already appears to be logged on with that account. Please try another account.')
                            else:
                                print('It seems you already have an account with us. Logging you in.\n')
                                can_enter = True
                        else:
                            print('Welcome to the store!\n')
                            self.Storefront.create_account(username, password) 
                            can_enter = True
                    user_pass_preset = False
            self.Storefront.add_current_customer(username, password)
            while (text != 'exit'):
                text = input("What would you like to do in the store? ")
                text = text.split()
                if text[0] == 'help':
                    print()
                    print('Available options:')
                    print("   'browse' : Tells you whats available in the store")
                    print("   'buy [item name]' : buys the item name from the store\n")
                    print("   'buy_sleep [item name]' : buys the item name from the store with a 10 sec sleep timer. Used for Testing.\n")
                if text[0] == 'browse':
                    print('Inventory: ')
                    response = self.Storefront.get_inventory()
                    print(response)
                if text[0] == 'buy':
                    response = self.Storefront.buy_item(text[1], username, password)
                    print(response)
                # This is a tester function for testing the semaphore. It includes a sleep function call to delay the purchase
                if text[0] == 'buy_sleep':
                    response = self.Storefront.buy_item(text[1], username, password, 10)
                    print(response)
                if text[0] == 'exit':
                    print('Goodbye!')
                    self.Storefront.exit_customer(username, password)
                    break
        finally:
            self.Storefront.exit_customer(username, password)

if __name__ == '__main__':
    try:
        args = parse_args()
        print('Entering store...')
        client = Customer(args)
        client.start_shopping()
    except (KeyboardInterrupt, EOFError):
        print('Goodbye!')