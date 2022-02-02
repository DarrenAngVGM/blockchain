# Ledger now works! Still manually create users, then create ledger, then call
# Ledger.transaction(payer, payee, payment) to make transactions.
"""At this point, the programmer is still keying in trxns. I need an individual user interface."""

import pandas as pd
from time import sleep


def main():
    A = User("A", 100)
    B = User("B", 100)
    C = User("C", 100)

    df = make_user_df([A, B, C])
    ledger = Ledger(df)

    print(ledger)

    ledger.transaction("A", "B", 200)  # The ledger system now declines transactions that go below the user's balance.

    # Generally, this seems to work quite well!
    ledger.transaction("A", "B", 100)
    print(ledger)

    ledger.transaction("B", "C", 150)  # But the bank (me, the programmer) is still keying in transactions.
    print(ledger)

    ledger.transaction("C", "A", 42.42)  # Next step: Let the users authenticate.
    print(ledger)


class User:

    def __init__(self, input_name, balance):
        self.name = input_name
        self.balance = balance

    def __repr__(self):
        return f"{self.name}: {self.balance} awesome coins\n"

    def update_balance(self, amount):
        """Takes var amount, a positive or negative int. Updates account balance of user."""
        self.balance += float(amount)


def make_user_df(users: list):
    """Takes a list of Users, adds their names and account balances to a df."""
    user_dict = dict()
    for user in users:
        user_dict[user.name] = [user.balance]

    df = pd.DataFrame.from_dict(user_dict)  # Names as columns, existing balances as first row
    return df


class Ledger:

    def __init__(self, ledger):
        """Takes an existing df and reads it into the class."""
        self.ledger = ledger

    def __repr__(self):
        print_dict = self.calculate_balances()
        print_str = ""
        for key in print_dict.keys():
            print_str = print_str + f"User {key} now has {print_dict[key]} awesome coins.\n"
        return f"*~-----------~*\n" \
               f"{len(self.ledger.index) - 1} transactions concluded.\n" + print_str + \
               "*~-----------~*"

    def calculate_balances(self):
        """Returns dict of user balances."""
        user_balances = self.ledger.sum(axis=0)
        return user_balances.to_dict()

    def transaction(self, payer_name, payee_name, payment):
        """Where payer and payee are names of Users, payer pays payee amount (in float).
        Updates the ledger amount for both Users."""

        # Check to see that payer and payee are in the ledger
        columns = self.ledger.columns
        if not {payer_name, payee_name}.issubset(columns):
            exit(f"Either {payer_name} or {payee_name} is not on the ledger. Check spelling plox")

        # Check to see that payment is a number, otherwise reject the transaction.
        transaction_no = len(self.ledger.index)
        if not isinstance(payment, (int, float)):
            exit(f"[!!!] Transaction of {payment} ACs from {payer_name} to {payee_name} failed. "
                 f"(Note: transaction amount be an int or float.)")

        # Make sure the payer has enough money in their account!
        payer_amount = self.calculate_balances()[payer_name]
        broke_flag = False
        if payer_amount - payment < 0:
            print(f"[!!!] Transaction of {payment} ACs from {payer_name} to {payee_name} declined. "
                  f"{payer_name} is broke lel.")
            broke_flag = True

        # Update ledger entries only if transaction successful
        if broke_flag is False:
            payer_loc, payee_loc = None, None  # Flag: If still 0, then names could not be found.

            column_count = 0  # Finds column no. for payer and payee. Extremely clunky, but ah well.
            for column in columns:
                if column == payer_name:
                    payer_loc = column_count
                elif column == payee_name:
                    payee_loc = column_count
                column_count += 1

            if payer_loc is None or payee_loc is None:  # Checks the flag
                exit("Could not find payer or payee in the ledger. Did you key in the name right?")

            # If the payer and payee can be found, create new row and append to df
            new_row = list()
            for i in range(len(columns)):
                if i == payer_loc:
                    new_row.append(-payment)
                elif i == payee_loc:
                    new_row.append(payment)
                else:
                    new_row.append(0)

            self.ledger.loc[transaction_no] = new_row
            print(f"Transaction no {transaction_no} successful: {payment} ACs from {payer_name} to {payee_name}")

        sleep(0.5)


if __name__ == "__main__":
    main()
