# Just users and existing balances. Manually key in users through class User(name, balance);
# use transaction(payer, payee, payment) to do transactions, print(User) to show user's balance.
"""Works, but allows people to pay more than they have. The trust here is that the users themselves will honour
their commitments to pay."""


def main():
    A = User("A", 100)
    B = User("B", 100)
    C = User("C", 100)

    transaction(A, B, 100)  # A pays B 100 awesome coins
    print(A, B, C)

    transaction(B, C, 200)  # B pays C 200 awesome coins
    print(A, B, C)

    transaction(C, A, 1000)  # Now C pays A 1000 awesome coins, which C does not have.
    print(A, B, C)  # Problem here: It allows balances to go negative!


class User:

    def __init__(self, input_name, balance):
        self.name = input_name
        self.balance = balance

    def __repr__(self):
        return f"{self.name}: {self.balance} awesome coins\n"

    def update_balance(self, amount):
        """Takes var amount, a positive or negative int. Updates account balance of user."""
        self.balance += float(amount)


def transaction(payer, payee, payment):
    """Where payer and payee are Users, payer pays payee amount (in float). Runs update_balance on both users."""
    if isinstance(payment, (int, float)):
        payer.update_balance(float(-payment))
        payee.update_balance(float(payment))
    else:
        exit(f"Transaction of {payment} from {payer.name} to {payee.name} failed. "
             f"(Note: transaction amount be an int or float.)")


if __name__ == "__main__":
    main()
