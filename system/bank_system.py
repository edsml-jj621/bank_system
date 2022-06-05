import pandas as pd
import datetime
from datetime import timedelta
timeFormat = '%d %b %Y %H:%M:%S'

__all__ = ['bankSystem', 'main']


class bankSystem():
    """Some operations functions in bank systems."""

    def __init__(self, df, ts):
        """Initialize the system and record dataframe for bank system.

        Parameters
        ----------

        df: pd.DataFrame
            store the data and ninformation of all clients' account
        ts: pd.DataFrame
            store the details of all transaction and operations history
        """
        self.df = df
        self.ts = ts

    def createAccount(self):
        """create an account in the bank system, the system will
        allocate the account number automatically, and required
        input of name, password, currency from users.
        """
        account = self.df.shape[0] + 10000000
        name = input("Please input your name: ")
        password = input("Please input the password: ")
        balance = 0.0
        currency = input("Please input the currency(HKD/USD/SGD): ")
        # load into the bank system dataframe
        self.df.loc[account] = [name, password, balance, currency]
        print('Account Created Successfully! Your account number is', account)

    def checkPassword(self):
        """This function checks the password when users try to access
        their account in the system for further operations. If the
        account is invalid or the password is incorrect,it will ask
        the user to input the account and password again. If all goes
        correctly, it will return the account number.

        Returns
        -------

        account: int
            account number
        """
        while True:
            account = input("Please input your account: ")
            account = int(account)
            # check the account in the system
            if self.df.index.isin([account]).any():
                password = input("Please input the password: ")
                # check the password
                if self.df.loc[account, 'password'] == password:
                    return account
                else:
                    print('Password Incorrect')
            else:
                print('Account Invalid')

    def depositMoney(self):
        """This function is fot deposit the money. It will first check
        the account and password of the users' input. And it asks the
        amount of money to be deposited. Finally, load the operations
        record into the bank system and operation history dataframe.
        """
        account = self.checkPassword()
        amount = input("Please input the amount to be deposited: ")
        self.df.loc[account, 'balance'] += float(amount)
        print('Deposit Money Successfully')

        name = self.df.loc[account, 'name']
        date = datetime.datetime.now().strftime(timeFormat)
        currency = self.df.loc[account, 'currency']
        operation = 'Deposit'
        self.ts.loc[self.ts.shape[0]] = [
            name, date, currency, operation, '+'+str(amount)]

    def withdrawMoney(self):
        """This is for money withdrawal. Check the account and password.
        Then check the times of withdrawal in the last 5 mins, and check
        the fund is sufficient. If all goes well, the withdrwal history
        will be wriiten in the system.
        """
        account = self.checkPassword()
        balance = self.df.loc[account, 'balance']
        name = self.df.loc[account, 'name']
        # check the num of times of withdrawal in last 5 mins
        if self.checkWithdraw(name):
            amount = input("Please input the amount to be withdrawn: ")
            # make sure the fund is suffiecient
            while float(amount)*1.01 > balance:
                print('Insufficient Fund, Balance =', balance)
                amount = input("Please input the amount to be withdrawn: ")
            currency = self.df.loc[account, 'currency']
            self.df.loc[(self.df['currency'] == currency) & (
                self.df['name'] == 'OSL_FEE'), 'balance'] += float(amount)*0.01
            self.df.loc[account, 'balance'] -= float(amount)
            self.df.loc[account, 'balance'] -= float(amount)*0.01
            print('Withdraw Money Successfully')
            # load into the history
            date = datetime.datetime.now().strftime(timeFormat)
            self.ts.loc[self.ts.shape[0]] = [
                name, date, currency, 'Withdrawal', '-'+amount]
            self.ts.loc[self.ts.shape[0]] = [name, date, currency,
                                             'Withdrawal FEE',
                                             '-'+str(float(amount)*0.01)]
            self.ts.loc[self.ts.shape[0]] = ['OSL_FEE', date,
                                             currency, 'Handling FEE',
                                             '+'+str(float(amount)*0.01)]

        else:
            print('Please try again later')

    def transferMoney(self):
        """To transfer the money between accounts. Check the target
        account is valid, check two accounts are of the same currency,
        check the balance is sufficient. If all goes well, it will
        write the history and operations in the system.
        """
        account = self.checkPassword()
        balance = self.df.loc[account, 'balance']
        name = self.df.loc[account, 'name']
        while True:
            to_account = input("Please input the account transfer to: ")
            to_account = int(to_account)
            # check the target account exists
            if self.df.index.isin([to_account]).any():
                # check two accounts are of the same currency
                currency = self.df.loc[account, 'currency']
                if currency == self.df.loc[to_account, 'currency']:
                    amount = input(
                        "Please input the amount to be transferred: ")
                    while float(amount)*1.01 > balance:
                        print('Insufficient Fund, Balance =', balance)
                        amount = input(
                            "Please input the amount to be withdrawn: ")
                    self.df.loc[(self.df['currency'] == currency) & (
                        self.df['name'] == 'OSL_FEE'),
                        'balance'] += float(amount)*0.01
                    self.df.loc[account, 'balance'] -= float(amount)
                    self.df.loc[account, 'balance'] -= float(amount)*0.01
                    self.df.loc[to_account, 'balance'] += float(amount)
                    print('Transfer Money Successfully')
                    # write the record into the operation history dataframe
                    to_name = self.df.loc[to_account, 'name']
                    date = datetime.datetime.now().strftime(timeFormat)
                    self.ts.loc[self.ts.shape[0]] = [
                        name, date, currency, 'Transfer Out', '-'+amount]
                    self.ts.loc[self.ts.shape[0]] = [
                        name, date, currency, 'Transfer FEE',
                        '-'+str(float(amount)*0.01)]
                    self.ts.loc[self.ts.shape[0]] = [
                        'OSL_FEE', date, currency,
                        'Handling FEE', '+'+str(float(amount)*0.01)]
                    self.ts.loc[self.ts.shape[0]] = [
                        to_name, date, currency, 'Transfer In', '+'+amount]

                    return False
                else:
                    print('Currency Different')
            else:
                print('Account Invalid')

    def listBalance(self):
        """List all the account for the particular user, showing the name
        of the users, the account currency and the balance.
        """
        name = input("Please input your name: ")
        # check whether the users exists
        if self.df['name'].isin([name]).any():
            print('---------------------------------')
            print(self.df.loc[self.df['name'] == name,
                  ['name', 'currency', 'balance']])
            print('---------------------------------')
        else:
            print("No Account Found")

    def displayTran(self):
        """To generate transaction statement for the particular user, it shows
        all the transaction record of all the accounts of the users, including
        the time, currency, operation type, and amount.
        """
        name = input("Please input your name: ")
        # check whether the users exists
        if self.ts['Name'].isin([name]).any():
            print('--------------------------------------------------------')
            print('Client Name:', name)
            print('--------------------------------------------------------')
            print(self.ts.loc[self.ts['Name'] == name, [
                  'Date', 'Currency', 'Operation', 'Amount']])
            print('--------------------------------------------------------')
        else:
            print("No Account Found")

    def checkWithdraw(self, user):
        """To check whether a single client do more than 5 withdrawals,
        limit to be reset every 5 minutes of last withdrawal. Return false
        if it exceeds 5 times, otherwise returns true.

        Parameters
        ----------

        user: string
            the name of the particular user, string

        Returns
        -------

        True or False: boolean
            the result of the checks
        """
        # time 5 mins earlier
        earlyDate = datetime.datetime.now() - timedelta(minutes=5)
        # last all withdrawal of the user
        lastallw = self.ts.loc[(self.ts['Operation'] == 'Withdrawal') & (
            self.ts['Name'] == user), 'Date'].values
        if len(lastallw) < 5:
            return True
        # last 5 withdrawal of the user
        lastFivew = lastallw[-5:]
        # def hte counter
        counter = 1
        for i in range(4):
            # check whether limit is reset
            time_break = datetime.datetime.strptime(
                lastFivew[i+1], timeFormat) - datetime.datetime.strptime(
                    lastFivew[i], timeFormat)
            if(time_break < timedelta(minutes=5)):
                counter += 1
        # if limit not reset and exceeds 5 times, return false
        lastDatew = datetime.datetime.strptime(lastFivew[-1], timeFormat)
        if (counter == 5) & (earlyDate < lastDatew):
            return False
        else:
            return True

    def mainMenu(self):
        """The main menu of the system. It will repeat until the user
        chooses to exit the system.
        """
        while True:
            print('\n\n------------OSL Bank System------------')
            print('1. Account Creation')
            print('2. Money Deposit')
            print('3. Money Withdrawal')
            print('4. Money Transfer')
            print('5. List Bank Account Balance')
            print('6. Display Transaction Statement')
            print('7. Exit')
            print('---------------------------------------\n')
            option = input('Please input your option: ')
            if option == '1':
                self.createAccount()
            elif option == '2':
                self.depositMoney()
            elif option == '3':
                self.withdrawMoney()
            elif option == '4':
                self.transferMoney()
            elif option == '5':
                self.listBalance()
            elif option == '6':
                self.displayTran()
            elif option == '7':
                return False


def main():
    """This is the main function.
    """
    # load the uesr information in the bank system
    dataFrame = pd.read_csv('system.csv', dtype=str, index_col=0)
    dataFrame['balance'] = dataFrame['balance'].astype(float)
    # load the operations record in the bank system
    tranState = pd.read_csv('record.csv', dtype=str, index_col=0)
    # create the system operator
    systemOper = bankSystem(dataFrame, tranState)
    # enter the main menu
    systemOper.mainMenu()
    # save all the record and information into the data system
    dataFrame.to_csv('system.csv')
    tranState.to_csv('record.csv')


if __name__ == "__main__":
    main()
