class Pharmacy:
    def __init__(self):
        self.medicines = {}  # Format: {name: {'price': x, 'quantity': y, 'supplier': z}}
        self.suppliers = {}  # Format: {supplier_name: contact}
        self.prescriptions = []  # List of {'customer': str, 'medicines': {name: qty}}

    def add_supplier(self, name, contact):
        self.suppliers[name] = contact
        print(f"✔️ Supplier '{name}' added.")

    def add_medicine(self, name, price, quantity, supplier):
        if name in self.medicines:
            self.medicines[name]['quantity'] += quantity
        else:
            self.medicines[name] = {
                'price': price,
                'quantity': quantity,
                'supplier': supplier
            }
        print(f"✔️ {quantity} units of {name} added (Supplier: {supplier}).")

    def display_stock(self):
        print("\n📦 Available Medicines:")
        if not self.medicines:
            print("No medicines in stock.")
            return
        for name, details in self.medicines.items():
            print(f"• {name} - ₹{details['price']} | Qty: {details['quantity']} | Supplier: {details['supplier']}")

    def sell_medicine(self, name, quantity):
        if name not in self.medicines:
            print("❌ Medicine not available.")
            return None
        if self.medicines[name]['quantity'] < quantity:
            print("⚠️ Not enough stock.")
            return None
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

    def record_prescription(self, customer, items):
        self.prescriptions.append({'customer': customer, 'medicines': items})
        print(f"📋 Prescription for {customer} recorded.")

    def show_suppliers(self):
        print("\n🔗 Registered Suppliers:")
        for name, contact in self.suppliers.items():
            print(f"• {name} - Contact: {contact}")


def main():
    shop = Pharmacy()
    while True:
        print("\n====== Pharmacy Management System ======")
        print("1. Add Supplier")
        print("2. Add Medicine")
        print("3. Show Stock")
        print("4. Sell Medicine")
        print("5. Generate Bill")
        print("6. Record Prescription")
        print("7. Show Suppliers")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Supplier name: ")
            contact = input("Contact info: ")
            shop.add_supplier(name, contact)

        elif choice == '2':
            name = input("Medicine name: ")
            price = float(input("Price: ₹"))
            qty = int(input("Quantity: "))
            supplier = input("Supplier name: ")
            shop.add_medicine(name, price, qty, supplier)

        elif choice == '3':
            shop.display_stock()

        elif choice == '4':
            name = input("Medicine to sell: ")
            qty = int(input("Quantity: "))
            shop.sell_medicine(name, qty)

        elif choice == '5':
            purchases = {}
            while True:
                name = input("Enter medicine (or 'done' to finish): ")
                if name.lower() == 'done':
                    break
                qty = int(input("Enter quantity: "))
                purchases[name] = qty
            shop.generate_bill(purchases)

        elif choice == '6':
            customer = input("Customer name: ")
            items = {}
            while True:
                name = input("Enter medicine for prescription (or 'done'): ")
                if name.lower() == 'done':
                    break
                qty = int(input("Enter quantity: "))
                items[name] = qty
            shop.record_prescription(customer, items)

        elif choice == '7':
            shop.show_suppliers()

        elif choice == '8':
            print("🔒 Exiting system. Thank you!")
            break

        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
