import json

class ProductionToolSelector:
    def __init__(self):
        self.tools = {
            'Stable Audio': {},
            'MusicGen (Meta)': {},
            'LocalGenerators': {},
            'Custom Synthesis': {}
        }
        self.preferences = {}

    def evaluate_tools(self):
        print("Evaluate the following tools based on capabilities, quality, latency, and integration.")
        for tool in self.tools.keys():
            print(f"- {tool}")

            capabilities = input(f"Evaluate capabilities for {tool}: ")
            quality = input(f"Evaluate quality for {tool}: ")
            latency = input(f"Evaluate latency for {tool}: ")
            integration = input(f"Evaluate integration for {tool}: ")

            self.tools[tool] = {
                'capabilities': capabilities,
                'quality': quality,
                'latency': latency,
                'integration': integration
            }

    def select_tool(self):
        print("Based on your evaluations, declare your preferred tool:")
        preferred_tool = input(f"Enter the name of the preferred tool: ")

        if preferred_tool in self.tools:
            self.preferences['preferred_tool'] = preferred_tool
            print(f"You have selected: {preferred_tool}")
        else:
            print("Selected tool is not valid.")

    def save_preferences(self):
        with open('barrot_production_preference.json', 'w') as json_file:
            json.dump(self.preferences, json_file, indent=4)

if __name__ == '__main__':
    selector = ProductionToolSelector()
    selector.evaluate_tools()
    selector.select_tool()
    selector.save_preferences()