import customtkinter as ctk

try:
    print("Attempting to create a CustomTkinter window...")
    
    # 1. Create the main window
    app = ctk.CTk()
    app.geometry("300x200")
    app.title("Test")

    # 2. Add a label
    label = ctk.CTkLabel(app, text="If you see this, CustomTkinter works!")
    label.pack(pady=20, padx=20)

    print("Window created. Starting mainloop()...")
    
    # 3. Show the window
    app.mainloop()

    print("Window closed.")

except Exception as e:
    print("\n--- AN ERROR OCCURRED ---")
    print(f"Error details: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to close this test...")