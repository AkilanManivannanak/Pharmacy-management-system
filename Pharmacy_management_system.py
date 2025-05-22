# pharmacy_management.py

class Pharmacy:
    def __init__(self):
        self.medicines = {}

    def add_medicine(self, name, price, quantity):
        if name in self.medicines:
            self.medicines[name]['quantity'] += quantity
        else:
            self.medicines[name] = {'price': price, 'quantity': quantity}
        print(f"✔️ {quantity} units of {name} added successfully.")

    def display_stock(self):
        print("\n📦 Available Medicines:")
        if not self.medicines:
            print("No medicines in stock.")
            return
        for name, details in self.medicines.items():
            print(f"• {name} - Price: ₹{details['price']} | Quantity: {details['quantity']}")

    def sell_medicine(self, name, quantity):
        if name not in self.medicines:
            print("❌ Medicine not available.")
            return

        if self.medicines[name]['quantity'] < quantity:
            print("⚠️ Not enough stock.")
            return

        total_price = self.medicines[name]['price'] * quantity
        self.medicines[name]['quantity'] -= quantity
        print(f"✅ Sold {quantity} units of {name}. Total: ₹{total_price}")
        return total_price

    def generate_bill(self, purchases):
        print("\n🧾 Generating Bill...")
        total = 0
        for name, qty in purchases.items():
            if name in self.medicines:
                price = self.medicines[name]['price']
                amount = price * qty
                print(f"{name} x{qty} = ₹{amount}")
                total += amount
        print(f"🟢 Total Bill Amount: ₹{total}")
        return total


def main():
    shop = Pharmacy()
    while True:
        print("\n====== Pharmacy Management System ======")
        print("1. Add Medicine")
        print("2. Show Stock")
        print("3. Sell Medicine")
        print("4. Generate Bill")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter medicine name: ")
            price = float(input("Enter price: "))
            qty = int(input("Enter quantity: "))
            shop.add_medicine(name, price, qty)

        elif choice == '2':
            shop.display_stock()

        elif choice == '3':
            name = input("Enter medicine to sell: ")
            qty = int(input("Enter quantity to sell: "))
            shop.sell_medicine(name, qty)

        elif choice == '4':
            purchases = {}
            while True:
                name = input("Enter medicine (or 'done' to finish): ")
                if name.lower() == 'done':
                    break
                qty = int(input("Enter quantity: "))
                purchases[name] = qty
            shop.generate_bill(purchases)

        elif choice == '5':
            print("🔒 Exiting system. Thank you!")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
