import Pyro4
import uuid

global username
global password

class Customer(object):
    def __init__(self):
        self._client_id = uuid.uuid4()
        self.Storefront = Pyro4.Proxy(f"PYRONAME:store.server")

    def start_shopping(self):
        try:
            text = ''
            can_enter = False
            ns = Pyro4.locateNS()
            while (text.lower() != 'y' and text.lower() != 'n'):
                text = input('Have you shopped with us before? (y/n)')
                text = text.lower()
                if text == 'n':
                    print('Please create an account')
                elif text == 'y':
                    print('Please login')
                else:
                    continue
                while (not can_enter):
                    username = input('Username: ')
                    password = input('Password: ')
                    is_exists = self.Storefront.check_account_exists(username, password)
                    is_shopping = self.Storefront.check_if_current_shopper(username, password)
                    if text == 'y':
                        if not is_exists:
                            print(f"Sorry, no account exists with Username: '{username}' and Password: '{password}'.\n")
                        else:
                            if not is_shopping:
                                print('Welcome to the store!\n')
                                can_enter = True
                            else:
                                print('We are sorry, someone already appears to be logged on with that account. Please try another account.')
                    if text == 'n':
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
            self.Storefront.add_current_customer(username, password)
            while (text != 'exit'):
                text = input("What would you like to do in the store? ")
                text = text.split()
                if text[0] == 'help':
                    print()
                    print('Available options:')
                    print("   'browse' : Tells you whats available in the store")
                    print("   'buy [item name]' : buys the item name from the store\n")
                if text[0] == 'browse':
                    print('Checking inventory...')
                    response = self.Storefront.browse()
                    [print(x) for x in response]
                if text[0] == 'buy':
                    response = self.Storefront.buy_item(text[1], username, password)
                    print(response)
                # This is a tester function for testing the semaphore. The remote function is idential to buy_item() except it also includes a sleep() function
                if text[0] == 'buy_sleep':
                    response = self.Storefront.buy_item_sleep(text[1], username, password)
                    print(response)
                if text[0] == 'exit':
                    print('Goodbye!')
                    self.Storefront.exit_customer(username, password)
                    break
        finally:
            self.Storefront.exit_customer(username, password)

if __name__ == '__main__':
    try:
        print('Entering store...')
        client = Customer()
        client.start_shopping()
    except (KeyboardInterrupt, EOFError):
        print('Goodbye! (:')
    