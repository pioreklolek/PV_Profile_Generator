from gui.app import GuiApp

if __name__ == "__main__":
    print("Starting PV Profile Generator GUI...")
    try:
        app = GuiApp()
        app.startApp()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()