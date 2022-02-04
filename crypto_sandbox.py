import pandas as pd
from time import sleep
from timeit import default_timer
from random import randint, random
import hashlib


def main():

    # LEDGER: The users are represented by columns, and the transactions by rows.
    """If you wish to change the number of users or existing transactions, just edit 'ledger.csv'!

    Format should be obvious; it's one negative value (payer) and one positive value (payee), with the same value
    (payment), for each row.

    (Note: I did not code for error handling when reading the csv. Please key in legit values, or I will be sad.) """

    df = pd.read_csv("ledger.csv", index_col=0)
    ledger = Ledger(df)

    # KEYS: The users' private and public keys are freshly generated every time the code is run.
    """These keys are used to generate the unique transaction data, for proof-of-work purposes.
    If you'd like to see the keys, insert the code: print(ledger.keys)"""

    # TRANSACTIONS: Each new transaction will call for authentication by the payer AND proof-of-work by a miner.
    """You can alter the 'difficulty' of the proof-of-work by looking for the proof_of_work() function below!
    Also, you're free to add or change transactions if you'd like. Format: ledger.transaction(payer, payee, amount)."""

    ledger.transaction("A", "B", 1.02)
    ledger.transaction("B", "C", 5.68)
    ledger.transaction("D", "A", 68.42)

    # FINAL STATUS OF THE LEDGER: Includes all valid transactions.
    """Note that this does not change the underlying csv fed into the program."""

    print(ledger)


def proof_of_work(unique_trxn_data, nonce):
    """[CHANGING DIFFICULTY: Look for the 'difficulty = X' row, and change X to another integer]

    The Bitcoin SHA256 proof-of-work. Takes transaction data, and requires the miner to find a nonce (number only
    used once) that will result in a SHA256 hash containing X zero bits in front of it.

    Because SHA256 is a cryptographic hash function, there is no better way to figure out the nonce than to brute
    force guess it. Computers do it really fast. In this demonstration, the program just guesses random numbers until
    a number somehow works.

    Feel free to change the number of zero bits required; you'll notice that the time taken to brute-force guess it
    increases exponentially with the number of zero bits. In my experience, the computer takes more than 10 minutes
    once there are 8 zero bits, at least under my really inefficient program. Bitcoin miners are expected to spend
    10 minutes doing their proof of work, and this is modulated by changing the number of zero bits required."""

    mine_attempt = unique_trxn_data * nonce  # This represents one brute force guess of the nonce.

    sha = hashlib.new("sha256")
    sha.update(str(mine_attempt).encode("ascii"))  # Converts the guess into bits and runs it through SHA256

    # Calibrates number of zero bits required at the front of the SHA256 hash
    difficulty = 6  # Change this to any integer you'd like, to see how the time taken changes!
    solution = "".join(["0" for i in range(difficulty)])

    if sha.hexdigest()[:difficulty] == solution:
        print(f"\nNonce for difficulty of {difficulty} zero bits found.\n"
              f"SHA256 hash is {sha.hexdigest()}")
        return True
    else:
        return False


def transaction_data(private_key, public_key, transaction_no, previous_hash):
    """Gathers a bunch of unique transaction data for hashing. See Pt II of bitcoin paper.
    (Note: For this demonstration, the unique transaction data is just an integer/number, so it may not be unique.
    In reality, it should be some type of hash.)"""

    to_convert = private_key * public_key * transaction_no * previous_hash
    trxn_data = 0
    for each_char in str(to_convert):
        if each_char.isdigit():
            trxn_data += int(each_char)
    return trxn_data


def miner(newest_hash):
    """Simulates a coin miner. Needs to brute-force guess the nonce, given a hash. Rewards are imaginary for now.
    (Note: This assumes that the miner will find a solution eventually. The program will run until it does.)"""

    guess_counter = 0
    start = default_timer()
    while True:
        nonce_attempt = random()
        print(f"Miner guesses {nonce_attempt}, this is guess number {guess_counter}")
        if proof_of_work(newest_hash, nonce_attempt) is True:
            end = default_timer()
            print(f"Time taken: {end - start}s")
            return True
        else:
            guess_counter += 1

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

    def calculate_balances(self):
        """Sums up each user's account balance and returns a dict in the format --> user: balance."""
        user_balances = self.ledger.sum(axis=0)
        return user_balances.to_dict()

    def generate_keys(self):
        """Creates dict in the format --> user: (private/secret key, public key).

        Everyone knows a user's public key, but not the private key. The public key must be derivable from the private
        key. In this simulation, we use a math formula to derive the public key. It'll probably be a hash in reality.

        Private key is a randomly-generated number. Again, in reality, this should be a unique hash.
        Public key is derived from taking the private key and dividing that number by the sum of its digits.

        (Note: While the private and public keys are stored on the ledger server in this simulation, in reality,
        the private key would be tagged to the users' accounts and kept secure there.)"""

        user_keys = dict()
        for user in self.users:
            private_key = randint(1000000000, 9999999999)

            private_sum = 0
            for digit in str(private_key):
                private_sum += float(digit)
            public_key = private_key / private_sum

            user_keys[user] = (private_key, public_key)
        return user_keys

    def transaction(self, payer_name, payee_name, payment):
        """Where payer and payee are names of users, payer pays payee amount (in float).
        Updates the ledger amount for both users."""

        checks_passed = True
        print(f"---\n"
              f"Attempted transaction: {payment} ACs from {payer_name} to {payee_name}.\n")

        # Check to see that payer and payee are in the ledger
        if not {payer_name, payee_name}.issubset(self.users):
            print(f"[TRANSACTION DECLINED] Either {payer_name} or {payee_name} is not on the ledger.")
            checks_passed = False

        # Check to see that payment is a number, otherwise reject the transaction.
        transaction_no = len(self.ledger.index)
        if not isinstance(payment, (int, float)):
            print(f"[TRANSACTION DECLINED] Transaction of {payment} ACs from {payer_name} to {payee_name} failed. "
                 f"(Note: transaction amount be an int or float.)")
            checks_passed = False

        # Make sure the payer has enough money in their account!
        payer_amount = self.calculate_balances()[payer_name]
        if payer_amount - payment < 0:
            print(f"[TRANSACTION DECLINED] Transaction of {payment} ACs from {payer_name} to {payee_name} declined. "
                  f"{payer_name} is broke. Sad.")
            checks_passed = False

        # Get authentication from the payer and payee if all checks passed
        auth_flag = False
        if checks_passed is True:
            auth_flag = self.authenticate(payer_name, payee_name, payment)

        # Update ledger entries only if transaction successful, SUBJECT TO PROOF OF WORK.
        if auth_flag is True:
            print("Authentication complete, transaction is valid.")
            sleep(0.5)

            payer_loc, payee_loc = None, None  # Flag: If still 0, then names could not be found.

            column_count = 0  # Finds column no. for payer and payee. Extremely clunky, but ah well.
            for column in self.users:
                if column == payer_name:
                    payer_loc = column_count
                elif column == payee_name:
                    payee_loc = column_count
                column_count += 1

            # Payer and payee will be found because of checks.
            # Form new row, to be appended to df if proof-of-work done.
            new_row = list()
            for i in range(len(self.users)):
                if i == payer_loc:
                    new_row.append(-payment)
                elif i == payee_loc:
                    new_row.append(payment)
                else:
                    new_row.append(0)

            # Calls for a miner to do the proof-of-work; this simulates the first miner to guess the nonce correctly.
            blockchain = self.generate_blockchain()
            solve_for = blockchain[-1]

            print("Calling on a miner to conduct proof-of-work...")
            sleep(0.5)
            solution = miner(solve_for)

            # Once proof-of-work is done, add the transaction to the ledger.
            if solution is True:
                self.ledger.loc[transaction_no] = new_row
                print(f"Transaction no {transaction_no} successful: {payment} ACs from {payer_name} to {payee_name}")

        sleep(0.5)

    def generate_blockchain(self):
        """Takes the ledger class and generates the sequence of hashes, with each transaction representing one 'block'.
         (Note: In reality, this would be terribly inefficient. Usually, a block contains multiple transactions.)"""

        blockchain = [1]  # Beyond the first row (the "genesis block") start hashing. Hash for genesis block is 1.
        for index, row in self.ledger.iterrows():
            prev_hash = 1
            if index > 0:  # Look for who paid (only entry which > 0)
                for item_tup in row.iteritems():
                    if item_tup[1] > 0:
                        private_key, public_key = self.keys[item_tup[0]]
                        transaction_no = index
                        hash_result = transaction_data(private_key, public_key, transaction_no, prev_hash)

                        blockchain.append(hash_result)
                        prev_hash = hash_result

        return blockchain

    def user_initiated_payment(self):
        """Simulates a user logging into the interface and attempting to make a payment."""

        payer_name = input("[PAYER'S SCREEN] Who are you heh (payer's name, exactly)\t")
        payee_name = input("[PAYER'S SCREEN] Who would you like to pay? (payee's name, exactly)\t")

        # Check if both payer and payee are on the ledger.
        if not {payer_name, payee_name}.issubset(self.ledger.columns):
            exit(f"Either {payer_name} or {payee_name} is not on the ledger.")

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
        """Simulates a payer agreeing to make a payment."""

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

        return True


if __name__ == "__main__":
    main()
