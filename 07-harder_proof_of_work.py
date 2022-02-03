"""Going to make a much harder problem this time."""

import pandas as pd
from time import sleep
from timeit import default_timer
from random import randint, random
import hashlib


def main():
    """Reads ledger csv into Ledger class and generates blockchain. (Note: You're free to call
    ledger.user_initiated_payment() or ledger.transaction() to simulate extra transactions. They will not alter the
    underlying csv/ledger, though the blockchain will increase in length.)"""

    df = pd.read_csv("07-ledger_genuine.csv", index_col=0)
    ledger = Ledger(df)

    ledger.transaction("A", "B", 1.02)
    ledger.transaction("B", "C", 5.68)
    ledger.transaction("D", "A", 68.42)
    print(ledger)


def proof_of_work(newest_hash, nonce):
    """A much harder proof of work: sha256. Starting with X zeroes"""
    mine_attempt = newest_hash * nonce
    sha = hashlib.new("sha256")
    sha.update(str(mine_attempt).encode("ascii"))
    solution_chars = [char for char in sha.hexdigest()]

    for i in range(6):  # Toy with this number to see how fast the computer really is!
        if solution_chars[i] != str(0):  # Once any of the first X chars is not 0, proof of work is not completed
            return False

    return True  # This catches only situations where the first X chars are 0s.


def miner(newest_hash):
    """Simulates a coin miner. Needs to solve for the nonce, given a hash. Rewards still imaginary."""
    guess_counter = 0
    start = default_timer()
    while True:
        nonce_attempt = random()
        print(f"Miner guesses {nonce_attempt}, this is guess number {guess_counter}")
        if proof_of_work(newest_hash, nonce_attempt) is True:
            end = default_timer()
            print(f"Time taken: {end - start}s")
            return nonce_attempt
        else:
            guess_counter += 1


def bad_hash(private_key, public_key, transaction_no, previous_hash):
    """A very very simple hash. See Pt II of bitcoin paper."""
    to_convert = private_key * public_key * transaction_no * previous_hash
    hash = 0
    for each_char in str(to_convert):
        if each_char.isdigit():
            hash += int(each_char)
    return hash


class Ledger:

    def __init__(self, ledger):
        """Takes an existing df and reads it into the class."""
        self.ledger = ledger
        self.users = self.ledger.columns
        self.keys = self.generate_keys()

    def __repr__(self):
        print_dict = self.calculate_balances()
        print_str = ""
        for key in print_dict.keys():
            print_str = print_str + f"User {key} now has {print_dict[key]} awesome coins.\n"
        return f"*~-----------~*\n" \
               f"{len(self.ledger.index) - 1} transactions concluded.\n" + print_str + \
               "*~-----------~*\n"

    def generate_keys(self):
        """Creates dict in the format --> user: (private/secret key, public key).
        Assume that only the user knows the private key; it's pretty hard to implement a p2p network on one device."""
        user_keys = dict()
        for user in self.users:
            private_key = randint(1000000000, 9999999999)

            private_sum = 0
            for digit in str(private_key):
                private_sum += float(digit)
            public_key = private_key / private_sum

            user_keys[user] = (private_key, public_key)
        return user_keys

    def calculate_balances(self):
        """Returns dict of user balances."""
        user_balances = self.ledger.sum(axis=0)
        return user_balances.to_dict()

    def transaction(self, payer_name, payee_name, payment):
        """Where payer and payee are names of Users, payer pays payee amount (in float).
        Updates the ledger amount for both Users."""

        print(f"---\n"
              f"Attempted transaction: {payment} ACs from {payer_name} to {payee_name}.\n")

        # Check to see that payer and payee are in the ledger
        if not {payer_name, payee_name}.issubset(self.users):
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

        # Get authentication from the payer and payee
        auth_flag = self.authenticate(payer_name, payee_name, payment)

        # Update ledger entries only if transaction successful, SUBJECT TO PROOF OF WORK.
        if broke_flag is False and auth_flag is True:
            payer_loc, payee_loc = None, None  # Flag: If still 0, then names could not be found.

            column_count = 0  # Finds column no. for payer and payee. Extremely clunky, but ah well.
            for column in self.users:
                if column == payer_name:
                    payer_loc = column_count
                elif column == payee_name:
                    payee_loc = column_count
                column_count += 1

            if payer_loc is None or payee_loc is None:  # Checks the flag
                exit("Could not find payer or payee in the ledger. Did you key in the name right?")

            # If the payer and payee can be found, create new row and append to df
            new_row = list()
            for i in range(len(self.users)):
                if i == payer_loc:
                    new_row.append(-payment)
                elif i == payee_loc:
                    new_row.append(payment)
                else:
                    new_row.append(0)

            # Needs valid proof of work for the new transaction to continue!
            blockchain = self.generate_blockchain()
            solve_for = blockchain[-1]
            solution = proof_of_work(solve_for, miner(solve_for))

            if solution is True:
                self.ledger.loc[transaction_no] = new_row
                print(f"Transaction no {transaction_no} successful: {payment} ACs from {payer_name} to {payee_name}")

        sleep(0.5)

    def generate_blockchain(self):
        """Takes the ledger class and generates the sequence of hashes; this is the blockchain we'll use."""
        blockchain = [1]  # Beyond the first row (the "genesis block") start hashing. Hash for genesis block is 1.
        for index, row in self.ledger.iterrows():
            prev_hash = 1
            if index > 0:  # Look for who paid (only entry which > 0)
                for item_tup in row.iteritems():
                    if item_tup[1] > 0:
                        private_key, public_key = self.keys[item_tup[0]]
                        transaction_no = index
                        hash_result = bad_hash(private_key, public_key, transaction_no, prev_hash)

                        blockchain.append(hash_result)
                        prev_hash = hash_result

        return blockchain

    def user_initiated_payment(self):
        payer_name = input("[PAYER'S SCREEN] Who are you lel (payer's name)\t")
        payee_name = input("[PAYER'S SCREEN] Who would you like to pay?\t")

        # Check if both payer and payee are on the ledger.
        if not {payer_name, payee_name}.issubset(self.ledger.columns):
            exit(f"Either {payer_name} or {payee_name} is not on the ledger. Check spelling plox")

        # If they are, then ask for payment amount.
        while True:
            payment = input(f"[PAYER'S SCREEN] How much? Your current balance is "
                            f"{self.calculate_balances()[payer_name]} ACs.")
            try:
                payment = float(payment)
                break
            except ValueError:
                print("Payment must be an integer or decimal")

        sleep(0.5)
        print("Cool, thanks!\n")
        self.transaction(payer_name, payee_name, payment)

    def authenticate(self, payer_name, payee_name, payment):
        """Simulates two decentralised users logging in and saying the transaction is legit.
        Returns True is both sides authenticate, False if either does not."""

        # Payer side (could be condensed into one nested if condition, but that's messy)
        sleep(0.5)
        payer_login = input(f"[{payer_name.upper()}'S SCREEN] Are you {payer_name}? (Type 'y' if you are)\t")
        if payer_login.lower() == "y":
            sleep(0.5)
            print(f"You currently have {self.calculate_balances()[payer_name]} ACs in your account.")
            payer_auth = input(f"Are you cool with making a transaction of {payment} ACs from your account to "
                               f"{payee_name}? (Type 'y' if you are)\t")
            if payer_auth.lower() == "y":
                print("Thank you!\n")
            else:
                print(f"Authentication by {payee_name} not given. Transaction declined.\n")
                return False
        else:
            print(f"Authentication by {payer_name} not given. Transaction declined.\n")
            return False

        # Payee side
        sleep(0.5)
        payee_login = input(f"[{payee_name.upper()}'S SCREEN] Are you {payee_name}? (Type 'y' if you are)\t")
        if payee_login.lower() == "y":
            sleep(0.5)
            payee_auth = input(f"Are you cool with receiving the transaction of {payment} ACs from {payee_name}'s "
                               f"account? (Type 'y' if you are)\t")
            if payee_auth.lower() == "y":
                print("Thank you!\n")
            else:
                print(f"Authentication by {payee_name} not given. Transaction declined.\n")
                return False
        else:
            print(f"Authentication by {payee_name} not given. Transaction declined.\n")
            return False

        return True

if __name__ == "__main__":
    main()
