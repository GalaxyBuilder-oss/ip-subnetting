import tkinter as tk
from tkinter import ttk, messagebox
from myipaddress import Subnet

class SubnettingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Subnetting Tool")
        
        # Input fields for IP address as separate octets
        self.ip_label = tk.Label(root, text="Enter IP Address (e.g., 192.168.1.1):", font=("Arial", 12, "bold"))
        self.ip_label.grid(row=0, column=0, columnspan=4, pady=10)

        # 4 Entry widgets for each octet of the IP
        self.ip_entries = []
        for i in range(4):
            entry = tk.Entry(root, width=5)
            entry.grid(row=1, column=i, padx=2)
            self.ip_entries.append(entry)

        # Mask label and entry
        self.mask_label = tk.Label(root, text="Enter Subnet Mask (e.g., 24):", font=("Arial", 12, "bold"))
        self.mask_label.grid(row=2, column=0, columnspan=4, pady=10)

        self.mask_entry = tk.Entry(root, width=5)
        self.mask_entry.grid(row=3, column=0, columnspan=4, pady=5)

        self.submit_button = tk.Button(root, text="Calculate", command=self.calculate_subnet)
        self.submit_button.grid(row=4, column=0, columnspan=4, pady=10)

        # Result Table
        self.tree = ttk.Treeview(root, columns=("Description", "Value"), show='headings')
        self.tree.heading("Description", text="Description")
        self.tree.heading("Value", text="Value")
        self.tree.grid(row=5, column=0, columnspan=4, pady=10)

        # Add Usable IPs Range Title
        self.usable_ips_label = tk.Label(root, text="Usable IPs Range", font=("Arial", 12, "bold"))
        self.usable_ips_label.grid(row=6, column=0, columnspan=4, pady=10)

        # Usable IPs Table with two columns
        self.usable_ips_tree = ttk.Treeview(root, columns=("Start IP", "End IP"), show='headings')
        self.usable_ips_tree.heading("Start IP", text="Start IP")
        self.usable_ips_tree.heading("End IP", text="End IP")
        self.usable_ips_tree.grid(row=7, column=0, columnspan=4, pady=10)

    def get_ip_from_entries(self):
        """Combine the values from the 4 IP entry fields into a single IP string."""
        ip_parts = [entry.get() for entry in self.ip_entries]
        try:
            # Validate and combine IP parts
            ip = ".".join(ip_parts)
            # Check if each octet is a valid number between 0 and 255
            if all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts):
                return ip
            else:
                raise ValueError("Each octet must be a number between 0 and 255.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return None

    def split_usable_ips_by_range(self, usable_ips, range_size):
        """Split usable IPs into groups of range_size."""
        return [usable_ips[i:i+range_size] for i in range(0, len(usable_ips), range_size)]

    def calculate_subnet(self):
        ip_input = self.get_ip_from_entries()
        mask_input = self.mask_entry.get()
        
        if not ip_input:
            return  # Exit if IP input is invalid

        try:
            mask = int(mask_input)
            subnet = Subnet(ip_input, mask)

            # Clear previous results
            if self.tree.get_children():
                for row in self.tree.get_children():
                    self.tree.delete(row)
            if self.usable_ips_tree.get_children():
                for row in self.usable_ips_tree.get_children():
                    self.usable_ips_tree.delete(row)

            formatted_usable_hosts = f"{subnet.num_addresses - 2:,}"  # Add commas to separate thousands

            # Populate results
            results = [
                ("Network Address", str(subnet.network_address)),
                ("Broadcast Address", str(subnet.broadcast_address)),
                ("Number of Usable Hosts", formatted_usable_hosts),
                ("Subnet Mask", str(mask)),
                ("IP Address Class", subnet.ip_class)
            ]
            for result in results:
                self.tree.insert("", "end", values=result)
            
            # List all usable IP addresses in ranges
            usable_ips = subnet.get_usable_ips()
            ip_ranges = self.split_usable_ips_by_range(usable_ips, 32)  # Split into blocks of 32 IPs
            for ip_range in ip_ranges:
                start_ip = ip_range[0]
                end_ip = ip_range[-1]
                self.usable_ips_tree.insert("", "end", values=(start_ip, end_ip))
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SubnettingApp(root)
    root.mainloop()
