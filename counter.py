from dash import html, Output, Input, State, callback
import pandas as pd
import os



class PortfolioCounter:
    def __init__(self, counter_file_path):
        self.counter_file_path = counter_file_path
        self._ensure_counter_file_exists()

    def _ensure_counter_file_exists(self):
        """Ensure the counter file exists and has the correct structure"""
        try:
            if not os.path.exists(self.counter_file_path):
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.counter_file_path), exist_ok=True)
                # Create new file with initial count
                self._create_new_counter_file()
            else:
                # Verify file is not empty and has correct structure
                try:
                    df = pd.read_csv(self.counter_file_path)
                    if 'count' not in df.columns or df.empty:
                        self._create_new_counter_file()
                except:
                    # If there's any error reading the file, recreate it
                    self._create_new_counter_file()
        except Exception as e:
            print(f"Error initializing counter file: {e}")
            self._create_new_counter_file()

    def _create_new_counter_file(self):
        """Create a new counter file with initial count of 0"""
        df = pd.DataFrame({'count': [0]})
        df.to_csv(self.counter_file_path, index=False)

    def get_counter_component(self):
        return html.Div(
            [
                html.Span("📊", style={"fontSize": "24px"}),
                html.Div(
                    [
                        "Portfolio Pilot ha analizzato",
                        html.Br(),
                        html.Span(
                            id="portfolio-count",
                            children="0",
                            style={"fontWeight": "bold"}
                        ),
                        " portafogli"
                    ],
                    style={"fontSize": "14px"}
                )
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "gap": "10px",
                "backgroundColor": "white",
                "padding": "12px 20px",
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                "width": "fit-content"
            },
            className="counter-component"  # Aggiungiamo una classe per il targeting CSS
        )
    def register_callbacks(self, app):
        @app.callback(
            Output("portfolio-count", "children"),
            Input("portfolio-toast", "is_open"),
            State("portfolio-count", "children"),
            prevent_initial_call=True
        )
        def update_counter(is_open, current_count):
            if not is_open:  # If is_open is False, don't update the counter
                return current_count or "0"

            try:
                df = pd.read_csv(self.counter_file_path)
                if 'count' not in df.columns or df.empty:
                    df = pd.DataFrame({'count': [0]})
                new_count = df['count'].iloc[0] + 1
                df = pd.DataFrame({'count': [new_count]})
                df.to_csv(self.counter_file_path, index=False)
                return str(new_count)
            except Exception as e:
                print(f"Error updating counter: {e}")
                return current_count or "0"

        @app.callback(
            Output("portfolio-count", "children", allow_duplicate=True),
            Input("url", "pathname"),
            prevent_initial_call=True
        )
        def initialize_counter(_):
            try:
                df = pd.read_csv(self.counter_file_path)
                if 'count' not in df.columns or df.empty:
                    self._create_new_counter_file()
                    return "0"
                return str(df['count'].iloc[0])
            except Exception as e:
                print(f"Error reading counter: {e}")
                self._create_new_counter_file()
                return "0"